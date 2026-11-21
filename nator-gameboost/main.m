#import <Foundation/Foundation.h>
#include <stdint.h>
#if __has_include(<libproc.h>)
#include <libproc.h>
#else
/* Some patched iPhoneOS SDKs omit libproc.h; these public C signatures
   match the system libproc ABI. No kernel call or privilege bypass. */
#define PROC_ALL_PIDS 1
#define PROC_PIDPATHINFO_MAXSIZE 4096
extern int proc_listpids(uint32_t type, uint32_t typeinfo, void *buffer, int buffersize);
extern int proc_pidpath(int pid, void *buffer, uint32_t buffersize);
#endif
#include <sys/resource.h>
#include <signal.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>

static volatile sig_atomic_t running = 1;
static void stopDaemon(int sig) { (void)sig; running = 0; }

static NSDictionary *config(void) {
    NSDictionary *p = [NSDictionary dictionaryWithContentsOfFile:@"/var/mobile/Library/Preferences/com.nator.gameboost.plist"];
    if (![p isKindOfClass:[NSDictionary class]]) p = @{};
    return @{@"Enabled":p[@"Enabled"] ?: @YES,
             @"BoostMode":p[@"BoostMode"] ?: @1,
             @"ReduceBackgroundApps":p[@"ReduceBackgroundApps"] ?: @NO,
             @"GameBundleIDs":p[@"GameBundleIDs"] ?: @"com.dts.freefireth,com.activision.callofduty.shooter,com.tencent.ig"};
}
static NSSet *gameIDs(NSDictionary *p) {
    id s = p[@"GameBundleIDs"];
    if (![s isKindOfClass:[NSString class]]) return [NSSet set];
    NSMutableSet *ids = [NSMutableSet set];
    for (NSString *item in [(NSString *)s componentsSeparatedByString:@","]) {
        NSString *bid = [[item stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]] lowercaseString];
        if (bid.length > 2 && bid.length < 180) [ids addObject:bid];
    }
    return ids;
}
static int targetNice(NSDictionary *p) {
    switch ([p[@"BoostMode"] intValue]) {
        case 0: return -1;
        case 2: return -5;
        default: return -3;
    }
}
/* Read the app's real bundle identifier; never adjust a system daemon. */
static NSArray *userApps(void) {
    int capacity = proc_listpids(PROC_ALL_PIDS, 0, NULL, 0);
    if (capacity <= 0) return @[];
    capacity += 4096;
    pid_t *pids = calloc(1, (size_t)capacity);
    if (!pids) return @[];
    int bytes = proc_listpids(PROC_ALL_PIDS, 0, pids, capacity);
    NSMutableArray *apps = [NSMutableArray array];
    for (int i = 0; i < bytes / (int)sizeof(pid_t); ++i) {
        pid_t pid = pids[i];
        if (pid <= 1 || pid == getpid()) continue;
        char buf[PROC_PIDPATHINFO_MAXSIZE] = {0};
        if (proc_pidpath(pid, buf, sizeof(buf)) <= 0) continue;
        NSString *path = [NSString stringWithUTF8String:buf];
        NSRange range = [path rangeOfString:@".app/"];
        if (range.location == NSNotFound) continue;
        NSString *bundle = [path substringToIndex:range.location + 4];
        NSDictionary *info = [NSDictionary dictionaryWithContentsOfFile:[bundle stringByAppendingPathComponent:@"Info.plist"]];
        NSString *bid = [info[@"CFBundleIdentifier"] isKindOfClass:[NSString class]] ? [info[@"CFBundleIdentifier"] lowercaseString] : nil;
        if (bid.length) [apps addObject:@{@"pid":@(pid), @"path":path, @"id":bid}];
    }
    free(pids);
    return apps;
}
static void restore(NSMutableDictionary *changed) {
    for (NSNumber *key in changed) {
        pid_t pid = (pid_t)key.intValue;
        NSDictionary *old = changed[key];
        char buf[PROC_PIDPATHINFO_MAXSIZE] = {0};
        if (proc_pidpath(pid, buf, sizeof(buf)) <= 0) continue;
        NSString *path = [NSString stringWithUTF8String:buf];
        if ([path isEqualToString:old[@"path"]])
            setpriority(PRIO_PROCESS, pid, [old[@"nice"] intValue]);
    }
    [changed removeAllObjects];
}
static void daemonRun(void) {
    signal(SIGTERM, stopDaemon);
    signal(SIGINT, stopDaemon);
    NSMutableDictionary *changed = [NSMutableDictionary dictionary];
    NSMutableSet *failures = [NSMutableSet set];
    NSLog(@"Nator GameBoost started: no jetsam, thermal or GPU overrides");
    while (running) {
        @autoreleasepool {
            NSDictionary *p = config();
            NSSet *targets = gameIDs(p);
            NSArray *apps = userApps();
            BOOL active = NO;
            NSMutableSet *alive = [NSMutableSet set];
            for (NSDictionary *a in apps) {
                [alive addObject:a[@"pid"]];
                if ([targets containsObject:a[@"id"]]) active = YES;
            }
            active = active && [p[@"Enabled"] boolValue];
            if (!active) restore(changed);
            else {
                BOOL backgrounds = [p[@"ReduceBackgroundApps"] boolValue];
                for (NSDictionary *a in apps) {
                    BOOL game = [targets containsObject:a[@"id"]];
                    if (!game && !backgrounds) continue;
                    int desired = game ? targetNice(p) : 5;
                    pid_t pid = (pid_t)[a[@"pid"] intValue];
                    errno = 0;
                    int current = getpriority(PRIO_PROCESS, pid);
                    if (current == -1 && errno) continue;
                    NSNumber *key = a[@"pid"];
                    NSDictionary *old = changed[key];
                    if (old && ![old[@"path"] isEqualToString:a[@"path"]]) {
                        [changed removeObjectForKey:key]; old = nil;
                    }
                    if (!old && (game ? current <= desired : current >= desired)) continue;
                    if (current == desired) continue;
                    if (setpriority(PRIO_PROCESS, pid, desired) == 0) {
                        if (!old) changed[key] = @{@"nice":@(current), @"path":a[@"path"]};
                    } else {
                        NSString *idErr = [NSString stringWithFormat:@"%@/%d",a[@"id"],errno];
                        if (![failures containsObject:idErr]) {
                            [failures addObject:idErr];
                            NSLog(@"Nator: no permission to reprioritize %@, errno=%d", a[@"id"], errno);
                        }
                    }
                }
                for (NSNumber *key in [changed allKeys])
                    if (![alive containsObject:key]) [changed removeObjectForKey:key];
            }
        }
        for (int i=0;i<5 && running;++i) sleep(1);
    }
    restore(changed);
}
static void display(BOOL all) {
    NSDictionary *p = config();
    NSSet *ids = gameIDs(p);
    printf("Nator GameBoost | enabled=%s | game nice=%d | reduce other apps=%s\n",
      [p[@"Enabled"] boolValue]?"yes":"no", targetNice(p),[p[@"ReduceBackgroundApps"] boolValue]?"yes":"no");
    printf("Configured: %s\n", [[ids.allObjects componentsJoinedByString:@", "] UTF8String]);
    int total = 0;
    for (NSDictionary *a in userApps()) {
        BOOL game = [ids containsObject:a[@"id"]];
        if (!all && !game) continue;
        pid_t pid = (pid_t)[a[@"pid"] intValue];
        errno = 0;
        int n = getpriority(PRIO_PROCESS, pid);
        printf("%s pid=%d nice=%d bundle=%s\n",game?"[GAME]":"[APP]",pid,n,[a[@"id"] UTF8String]);
        if (game) total++;
    }
    if (!total) puts("No configured game process running.");
    puts("No jetsam/memory limit changes. iOS Game Mode controls foreground CPU/GPU scheduling.");
}
int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc > 1 && strcmp(argv[1],"--daemon") == 0) daemonRun();
        else if (argc > 1 && strcmp(argv[1],"status") == 0) display(NO);
        else if (argc > 1 && strcmp(argv[1],"list") == 0) display(YES);
        else puts("Usage: natorgamerd status | list | --daemon");
    }
    return 0;
}
