
# Pycharm Remote Debugging

This howto describes how to have a remote python process connect to your Pycharm IDE for debugging

This process would generally work regardless of docker, k8s, or any other process management method.
Generally the only requirements are Pycharm Professional and network connectivity from the python app
(client) to the python ide/debugger (server)

Its also assumed you already have a voltha build environment on the vm or machine your running the IDE,
with the proper env file sources, proto's build and docker images able to be created.



## Create a remote debug process configuration in the Pycharm IDE

This creates a runtime configuration that runs the remote debugger process rather than a local python process.

Click Tools -> Edit Configurations  
Click +, Add a Python Remote Debug configuration and name whatever makes sense  
Set Local host name to 0.0.0.0   This causes the debug server to listen on all IP  
Set Listen Port to 4444  
Path mappings: /home/foundry/source/voltha=/voltha   

Apply/OK  



## Copy the debugging library egg into your build environment

This egg exists in the deployment home of pycharm.  In my case its in /opt, but it could be anywhere.

~~~
cp /opt/pycharm-2018.1.4/debug-eggs/pycharm-debug.egg ~/source/voltha
~~~

Also in order for the IDE to properly link and reference the the egg, add it as a "Content Root"

Click File -> Settings  
Under Project: voltha  
  Project Structure  

 \+ Add Content Root

Navigate and select the pycharm-debug.egg file.



## Add code to main entrypoint to connect to debugger

Add the following code just below the __main__ check to connect your python client to the remote debugger.
Get the IP of the device running your IDE and use it in the code.  In my example my desktop is on 10.64.10.146.

~~~
if __name__ == '__main__':  
  import pydevd  
  pydevd.settrace('10.64.10.146', port=4444, stdoutToServer=True, stderrToServer=True)  
~~~


## Start the remote debug process 

This will start the 0.0.0.0:4444 listener on your desktop IDE, waiting for a connection.

Run -> Debug 'your debug config'  



## Modify the docker image build for voltha/vcore to include the egg

Change the docker/Docker.voltha file to copy in the new egg into the image and modify PYTHONPATH path to find it.  

Make the following change:  

~~~
# Bundle app source  
RUN mkdir /voltha && touch /voltha/__init__.py  
ENV PYTHONPATH=/voltha:/voltha/pycharm-debug.egg    ## Add addtional item after colon  
COPY common /voltha/common  
COPY voltha /voltha/voltha  
COPY pki /voltha/pki  
COPY pycharm-debug.egg /voltha/   ## New line  
~~~

Re-run make build or docker build to create your new voltha/vcore image.   Deploy that image using your method of choice 
(docker compose or kubectl apply)

When the new container is running execution will pause at the pydevd.settrace method call.  At this point the IDE will pause 
at the __main__ section prompting you to start the debug session.   Press the play button in the Debugger window to resume the
startup and logging of voltha.   Set breakpoints in code and inspect variables in Pycharm as needed.



