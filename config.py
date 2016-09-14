from fabric.api import *
from fabric.contrib.files import *


nodes = [
    {"node": "compute31", "login": "ebagdasa", "pass": "eb693eb693", 'ip': '192.168.9.31'},
    {"node": "compute32", "login": "ebagdasa", "pass": "eb693eb693", 'ip': '192.168.9.32'},

    {"node": "compute30", "login": "ebagdasa", "pass": "eb693eb693", 'ip': '192.168.9.30'},
    {"node": "compute20", "login": "ebagdasa", "pass": "sst", 'ip': '192.168.9.20'},
    {"node": "compute18", "login": "ebagdasa", "pass": "sst", 'ip': '192.168.9.18'},
    {"node": "compute17", "login": "ebagdasa", "pass": "sst", 'ip': '192.168.9.17'},
    {"node": "compute16", "login": "ebagdasa", "pass": "sst", 'ip': '192.168.9.16'},
]
port_1='2889'
port_2='3889'
full_hostname = 'fractus.cs.cornell.edu'
dir = '/home/ebagdasa/zoo'
disk_dir = '/mnt/eugene_disk'
data_dir = disk_dir + '/data'
zookeeper_location = dir+'/zookeeper-3.4.9'
zoo_cfg = zookeeper_location + '/conf/zoo.cfg'
url = 'http://apache.claz.org/zookeeper/stable/zookeeper-3.4.9.tar.gz'
config = """tickTime=2000
dataDir={data_dir}
clientPort=2182
initLimit=5
syncLimit=2
{servers_list}
"""


def modify_zookeper(servers):
    servers_list = ['server.{id}={server}:{port_1}:{port_2}'.format(id=i+1, server=x['ip'], port_1=port_1, port_2=port_2)
                    for i, x in enumerate(servers)]
    modified_config = config.format(data_dir=data_dir, servers_list='\n'.join(servers_list))
    # stop service
    # execute_zookeper(servers, 'stop')

    for i, server in enumerate(servers):
        host_string = '{0}.{1}'.format(server['node'], full_hostname)
        with settings(host_string=host_string, user=server['login'], password=server['pass']):
            run('echo "{conf}" > {cfg}'.format(conf=modified_config, cfg=zoo_cfg))
            run('rm -rf {0} && mkdir {0}'.format(data_dir))
            run('echo "{position}" > {myid}'.format(position=i+1, myid=data_dir+'/myid' ))

    # start
    execute_zookeper(servers, 'start')


def execute_zookeper(servers, command):
    for server in servers:
        host_string = '{0}.{1}'.format(server['node'], full_hostname)
        with settings(host_string=host_string, user=server['login'], password=server['pass']):
            with path("/opt/jdk1.7.0_67/bin"):
                # sudo('chown ebagdasa:sudo -R {0}'.format(zookeeper_location))
                run('{file} {command}'.format(file=zookeeper_location+'/bin/zkServer.sh', command=command))
                run('jps')


def cmd(servers, command, use_sudo=False, warn=False):
    response = []
    for server in servers:
        host_string = '{0}.{1}'.format(server['node'], full_hostname)
        with settings(host_string=host_string, user=server['login'], password=server['pass']):
            with path("/opt/jdk1.7.0_67/bin"):
                response.append({'server': server['node'], 'result': sudo(command,  warn_only=warn)
                if use_sudo else run(command, warn_only=warn)})
    return response


def prepare_memory(servers):
    for server in servers:
        host_string = '{0}.{1}'.format(server['node'], full_hostname)
        with settings(host_string=host_string, user=server['login'], password=server['pass']):
            with path("/opt/jdk1.7.0_67/bin"):
                if exists(disk_dir, use_sudo=True):
                    sudo('umount -f {0}'.format(disk_dir), warn_only=True)
                    sudo('rm -rf {0}'.format(disk_dir))
                sudo('mkdir {0}'.format(disk_dir), )
                sudo('mkfs.ext4 /dev/sdd -F')
                sudo('mount /dev/sdd {0}'.format(disk_dir))
                sudo('chmod 777 -R {0}'.format(disk_dir))


def main():
    amount = 1
    cmd1 = 'echo stat | nc localhost 2182 | grep Mode'

    execute_zookeper(nodes, 'stop')
    servers = nodes[:amount]
    # prepare_memory(servers[2:])
    modify_zookeper(servers)
    results = cmd(servers, cmd1, warn=True)
    for dic in results:
        if 'leader' in dic['result']:
            print dic['server']
    return 0

if __name__ == "__main__":
    main()
