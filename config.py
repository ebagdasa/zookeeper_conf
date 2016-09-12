from fabric.api import *


nodes = [
    {"node": "compute32", "login": "ebagdasa", "pass": "eb693eb693"},
    {"node": "compute31", "login": "ebagdasa", "pass": "eb693eb693"},
    {"node": "compute30", "login": "ebagdasa", "pass": "eb693eb693"},
    {"node": "compute29", "login": "ebagdasa", "pass": "eb693eb693"},
    {"node": "compute28", "login": "ebagdasa", "pass": "eb693eb693"},
    {"node": "compute27", "login": "ebagdasa", "pass": "eb693eb693"},
    {"node": "compute26", "login": "ebagdasa", "pass": "eb693eb693"},
    {"node": "compute25", "login": "ebagdasa", "pass": "eb693eb693"},
    {"node": "compute24", "login": "ebagdasa", "pass": "eb693eb693"},
]
port_1='2889'
port_2='3889'
full_hostname = 'fractus.cs.cornell.edu'
dir = '/home/ebagdasa/zoo'
data_dir = dir + '/data'
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
    servers_list = ['server.{id}={server}:{port_1}:{port_2}'.format(id=i+1, server=x['node'], port_1=port_1, port_2=port_2)
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
                run('{file} {command}'.format(file=zookeeper_location+'/bin/zkServer.sh', command=command))
                run('jps')


def main():
    amount = 7
    execute_zookeper(nodes, 'stop')
    servers = nodes[:amount]
    modify_zookeper(servers)
    return 0

if __name__ == "__main__":
    main()
