# Nexxera DevOps

Este projeto tem como intuito de criar soluções a problemas propostos pela equipe de DevOps Nexxera. Você irá encontrar scripts de automção `Ansible` e informações de como replicar os experimentos. 

## 1. Deploy de Updates via FTP

Para esse problema temos o objetivo de pegar um arquivo com recebimento diário em um `ftp_server` e fazer Deploy dessa aplicação em um `target_server`.

O primeiro passo que devemos fazer é escolher onde iremos fazer a detecção de novos arquivos no FTP. Ela poderia ser feita de algumas maneiras

- Cronjob em uma instância Linux
    
    O cronjob poderia ser fácilmente colocado junto com o FTP caso fosse um SFTP e tivessemos acesso a ele. No pior dos casos, existiria uma instância ligada pura e exclusivamente para isso. Essa solução seria ruim, pois estamos deixando a maior parte do recurso computacional e memória ocioso para algo que vai ser executado apenas 1 vez ao dia.

- AWS Lambda + AWS Cloudwatch Events

    O problema da solução anterior é resolvido com uma execução Serverless. Neste caso estou usando AWS Lambda + AWS Cloudwatch Events como exemplo, mas poderia ser qualquer serviço que execute esse propósito: executar uma aplicação, cobrar apenas pela execução e dar meios de executar periódicamente. Com isso economizamos recursos computacionais e consequentemente financeiros.

- Job periódico no CI/CD (Jenkins/Gitlab CI/ouutros)

    A terceira opção é utilizar um CI/CD que, preferencialmente, já está instalado e é usado para outras operações e com isso apenas adicionamos um Job. O CI/CD ficará encarregado de executar nosso script diáriamente e com isso utilizamos recursos que já estão disponíveis pronto para esse tipo de execução.

Algumas perguntas que devemos responder é: `Essa aplicação pode ficar fora do ar por um breve momento?` Se a resposta for não, temos que responder `Posso executar duas instâncias dessa aplicação ao mesmo tempo por um breve momento?`.

Temos que respondê-las para definir como será feita a atualização. Normalmente para uma aplicação não-crítica iremos desligar a aplicação que está rodando, realizar a update e reiniciar a aplicação. Porém, existe um tipo de deployment chamado blue/green(também chamado de red/black) onde em um determinado momento temos as duas versões rodando (antiga e nova) e se tudo ocorreu bem, desativamos a versão antiga assim ficando apenas com a nova. Esse tipo de update geralmente é feita em aplicações que tem um balanceador de carga na frente para não perder nenhuma requisição nesse meio tempo.

Nesse caso irei considerar que a aplicação `NÃO` é crítica e/ou o deploy ocorrerá em um horário que a aplicação não é necessária.

Com o problema de quando e onde vai ser a execução, temos que definir como vai ser o empacotamento da aplicação recebida pelo FTP. Primeiro de tudo, iremos criar uma imagem de Docker para essa aplicação ou não? Quero dizer, podemos executar a aplicação de forma direta nomeando o processo, ou até mesmo através do `systemctl` do Linux e transformar a aplicação em um serviço mas, na minha opinião, a melhor forma é fazer uma imagem `Docker` e executar em `containers`.

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

Primeiro de tudo é necessário instalar o Minishift e isso depende de qual sistema operacional você está usando.

No meu caso, eu uso Arch Linux, porém irei linkar os tutoriais de instalação caso seu sistema operacional seja diferente.

1. Configurar ambiente de virtualização

    Siga os passos em: https://docs.okd.io/3.11/minishift/getting-started/setting-up-virtualization-environment.html dependendo do seu OS.

    No final do processo, inicie o `libvirtd`:
    ```
    $ sudo systemctl start libvirtd
    ```

    Esse ultimo passo é necessário sempre que for iniciar o Minishift a não ser que você habilite o serviço a iniciar junto com o computador. Se você desejar fazer isso é só digitar ``` sudo systemctl enable libvirtd```

2. Instalar Minishift.
   
   Siga as instruções em https://docs.okd.io/3.11/minishift/getting-started/installing.html.

   No geral, você irá instalar o pacote `minisfhit` no seu gerenciador de pacotes.

3. Iniciando o Minishift.
    
    Para iniciar a máquina virtual, digite o seguinte comando:
    ```
    $ minishift start
    ```
    Ele irá checkar todos os pacotes, configurar a aplicação, docker, a maquina virtual, openshift, rede, etc. Caso ocorra algum erro, verifique se tudo foi instalado corretamente, e todos os pré-requisitos estão rodando normalmente.

    Após a inicialização, você vai querer utilizar o comando `oc` para se comunicar com o Openshift. Para fazer isso basta executar o seguinte comando:
    ```
    $ eval $(minishift oc-env)
    ```
    Com isso, ele irá configurar o PATH na sessão do terminal que você ta rodando e assim permitir você ir para os próximos passos.

4. Iniciando o container com Nginx.
   
   Resolvi criar um Dockerfile nesse respositório que adiciona o arquivo `info.json` no root do nginx. Por esse motivo, fica fácil de criar um container usando o Github.

   Para criar um projeto e uma nova aplicação rodando nginx com o website estático, rode o seguinte comando:
    ```
    $ oc new-app https://github.com/flametuner/nexxera_devops.git --strategy=docker --context-dir=openshift --name=nexxera
    ```
    Podemos ver o serviço rodando usando os comandos ```oc status``` e ```oc get pods```. Porém para acessar ele, precisamos expor a porta, que no caso do Dockerfile é a 8081:
    ```
    $ oc expose svc nexxera --port=8081
    ```
    Com a porta exposta, a coisa mais simples a se fazer para acessar no navegador é digitar o seguinte comando e acessar o arquivo `info.json`:
    ```
    $ minishift openshift service nexxera --in-browser
    ```

    No meu caso, a URL ficou http://nexxera-myproject.192.168.42.232.nip.io/info.json

    ![](https://i.imgur.com/TgyTpFp.png)
