#! /home/ansible/.venv/bin/python
# - * - coding: utf-8 - * -

"""LOG-GATEHER-CLI CLI.
Usage:[]
    log-gather.py copylog --host=<kn> [--program=<kn>]
    log-gather.py packlog --host=<kn> [--program=<kn>]
    log-gather.py cleanlog  --host=<kn> [--program=<kn>]
    log-gather.py -h | --help
    log-gather.py --version

Options:
    copylog                  cp remote log file to java2 tmp dir.
    packlog                  compress log file to tar.gz
    cleanlog                 clean old log file in local path.
    --host=<kn>              input host name,include java1,java2,java3,and java4.
    --program=<kn>           input program name ,for example spring, play and so on.
    -h, --help               display this help and exit.
    --version                output version information and exit.

"""

from docopt import docopt
from action import rsync_log


def action_route(doc_args):
    if doc_args.get("copylog"):
        if doc_args.get("--host") == 'all_play_spring':
            rsync_log.all_play_spring()
        elif doc_args.get("--host") == 'allspring':
            rsync_log.allspring()
        elif doc_args.get("--host") == 'allplay':
            rsync_log.allplay()
        else:
            rsync_log.CpLogTask(doc_args.get("--host"), doc_args.get("--program"))       
    elif doc_args.get("packlog"):
        if doc_args.get("--host") == 'all_play_spring':
            rsync_log.pack_all_play_spring()
        elif doc_args.get("--host") == 'allspring':
            rsync_log.pack_allspring()
        elif doc_args.get("--host") == 'allplay':
            rsync_log.pack_allplay()
        else:        
            rsync_log.PackLog(doc_args.get("--host"), doc_args.get("--program"))
    elif doc_args.get("cleanlog"):
        if doc_args.get("--host") == 'all_play_spring':
            rsync_log.CleanlallSpringPlayLog()
        elif doc_args.get("--host") == 'allspring':
            rsync_log.CleanallSpringLog()
        elif doc_args.get("--host") == 'allplay':
            rsync_log.CleanallPlayLog()    
        else:
            rsync_log.CleanOld_log(doc_args.get("--host"), doc_args.get("--program"))
    else:
        print("An unreasonable parameters")


if __name__ == '__main__':
    args = docopt(__doc__, version='LOG-GATEHER-CLI 1.0')
    action_route(args)