A] First Time setup
  a)Setting up Docker Desktop
    Install Docker Desktop from below website and register with your credentials
    https://docs.docker.com/desktop/setup/install/windows-install/

   b) Copy the code from github
    git clone https://github.com/pradeepgodi/bbdocker.git 

   c) Go to the above folder and execute the below commands in the terminal
        docker-compose up --build 
   d) Verify that in Docker Desktop the container is up and running

   e) You should see the webpage on the browser http://127.0.0.1:5000      


B] Updating existing code when the backend is updated/modified. Start the Docker Desktop application
    a) Get the latest from github
        git pull origin master

    b) Remove the existing docker container. Verify that the container is removed from the Docker Desktop
     docker-compose down -v
 
    c) Create a new container. Verify that a new container is added from the Docker Desktop
       docker-compose up --build 
    
    d) To stop the container
       using command : Ctrl + C 
      On Docker desktop : Go to container section/menu and stop the container
      You should not see the webpage on the browser http://127.0.0.1:5000     


C] To download libraries into wheelhouse
PS E:\BB\bb_api_service\bb_dockerized> pip download -r .\app\requirements.txt -d wheelhouse



