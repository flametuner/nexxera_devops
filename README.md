# Nexxera DevOps

Este projeto tem como intuito de criar soluções a problemas propostos pela equipe de DevOps Nexxera. Você irá encontrar scripts de automção `Ansible` e informações de como replicar os experimentos. 

## 1. Deploy de Updates via FTP

Para esse problema temos o objetivo de pegar um arquivo com recebimento diário em um `ftp_server` e fazer Deploy dessa aplicação em um `target_server`.

O primeiro passo que devemos fazer é escolher onde iremos fazer a detecção de novos arquivos no FTP. Ela poderia ser feita de algumas maneiras

- Cronjob em uma instância Linux
- AWS Lambda + AWS Cloudwatch Events
- Job periódico no CI/CD (Jenkins/Gitlab CI/ouutros)

O cronjob poderia ser fácilmente colocado junto com o FTP caso fosse um SFTP e tivessemos acesso a ele. No pior dos casos, existiria uma instância ligada pura e exclusivamente para isso. Essa solução seria ruim, pois estamos deixando a maior parte do recurso computacional e memória ocioso para algo que vai ser executado apenas 1 vez ao dia.

Isso é resolvido com uma execução Serverless. Neste caso estou usando AWS Lambda + AWS Cloudwatch Events como exemplo, mas poderia ser qualquer serviço que execute esse propósito: executar uma aplicação, cobrar apenas pela execução e dar meios de executar periódicamente. Com isso economizamos recursos computacionais e consequentemente financeiros.

A terceira opção é utilizar um CI/CD que, preferencialmente, já está instalado e é usado para outras operações e com isso apenas adicionamos um Job. O CI/CD ficará encarregado de executar nosso script diáriamente e com isso utilizamos recursos que já estão disponíveis pronto para esse tipo de execução.

Algumas perguntas que devemos responder é: `Essa aplicação pode ficar fora do ar por um breve momento?` Se a resposta for não, temos que responder `Posso executar duas instâncias dessa aplicação ao mesmo tempo por um breve momento?`.

Temos que respondê-las para definir como será feita a atualização. Normalmente para uma aplicação não-crítica iremos desligar a aplicação que está rodando, realizar a update e reiniciar a aplicação. Porém, existe um tipo de deployment chamado blue/green(também chamado de red/black) onde em um determinado momento temos as duas versões rodando (antiga e nova) e se tudo ocorreu bem, desativamos a versão antiga assim ficando apenas com a nova. Esse tipo de update geralmente é feita em aplicações que tem um balanceador de carga na frente para não perder nenhuma requisição nesse meio tempo.

Nesse caso irei considerar que a aplicação `NÃO` é crítica e/ou o deploy ocorrerá em um horário que a aplicação não é necessária.

Com o problema de quando e onde vai ser a execução, temos que definir como vai ser o empacotamento da aplicação recebida pelo FTP. Primeiro de tudo, iremos criar uma imagem de Docker para essa aplicação ou não? Quero dizer, podemos executar a aplicação de forma direta nomeando o processo, ou até mesmo através do `systemctl` do Linux e transformar a aplicação em um serviço mas, na minha opinião, a melhor forma é fazer uma imagem Docker e executar em containers.

Além de ser uma maneira muito mais fácil pois não é necessário se preocupar em qual ambiente está sendo executado o container, também é muito simples utilizar orquestradores de container e configurar detalhes como quantidade de réplicas de uma maneira simples.

### Ferramenta utilizada

Eu poderia utilizar Shell Script como maneira de automatizar esse processo, porém eu prefiro utilizar a ferramenta `Ansible` que além de executar um script ela tenta manter o estado que o script está, ou seja, se em algum momento algo for alterado ela volta ao estado desejado. 

### Solução

Com `Ansible` irei conectar no servidor destino, instalar Docker, criar uma imagem e instalar o container.

### Pré-requisitos

- Instalar Ansible
- Configurar dados do servidor destino em `hosts`
- Instalar roles externas com o comando ```ansible-galaxy install -r requirements.yml```
### Variáveis:

- `app_name`: nome da aplicação
- `file_name`: nome do arquivo (poderia ser facilmente estendido para *prefix_file_name*)
- `ftp_url`: link para ftp. ex: ftp://user:password@ftpserver/

Para mudar as variáveis, você pode alterar direto no arquivo ou sobreescreve-las adicionando o parametro no comando abaixo `--extra-vars='<var_name1>=<var1> <var_name2>=<var2>'`

### O que o script faz:

1. Conecta ao servidor destino
2. Faz download do arquivo de update do FTP
3. Instala o Docker
4. Cria uma imagem docker com o arquivo
5. Cria/atualiza um container com a imagem nova
6. Limpa containers e imagens

Para executar o script é só digitar os seguintes comandos:
```
$ ansible-playbook -i hosts main.yml
```

Após fazer uma update em `hello_word_java`, commitei e enquanto rodava o script tirei print do que acontecia nas logs:

![](https://i.imgur.com/WTJuAun.png)

## 2. Openshift Deploy Nginx

Instalar o Minishift

```
$ oc new-app https://github.com/flametuner/nexxera_devops.git --strategy=docker --context-dir=openshift --name=nexxera
```

```
$ oc expose svc nexxera --port=8081
```

Acessar em: http://nexxera-myproject.192.168.42.232.nip.io/info.json
