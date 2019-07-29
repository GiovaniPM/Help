# How to install help

## Setup
>Get the file setup.sh on this repository and copy to your projects dir
>
>``` dos
>./projects
>|   setup.sh
>|
>+---/Help
>         <files replicated>
>```
> 
>To run:
>``` bash
>./setup.sh
>```

## Architeture
>``` dos
>~
>|   .bash_aliases
>|   .bash_history
>|   .bash_profile
>|   .bashrc
>|   .gitconfig
>|   .gitignore
>|   download.sh
>|   upload.sh
>|   <...>
>+---projects/
>|   |   <...>
>|   +---<repository>/
>|   |   |   setup.sh
>|   |   |   <...>
>|   |   +---<...>/
>|   +---<...>/
>+---<...>/
>```

## Run download
>To run:
>``` bash
>download <repository>
>```

## Run upload
>To run:
>``` bash
>upload
>```
