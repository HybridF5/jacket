FROM 162.3.160.50:5000/tempest:latest

MAINTAINER laoyi <yibo_grace@163.com>

RUN yum install -y java
RUN yum install -y openssh-server

RUN mkdir -p /var/run/sshd

RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N ''

# Set user jenkins to the image
RUN useradd -m -d /home/jenkins -s /bin/sh jenkins &&\
    echo "jenkins:jenkins" | chpasswd

RUN chmod 777 /etc/tempest/ -R
RUN chown jenkins:jenkins /tempest/ -R


# Standard SSH port
EXPOSE 22

# Default command
CMD ["/usr/sbin/sshd", "-D"]

