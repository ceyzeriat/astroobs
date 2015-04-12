# README #

Python code repository for Astronomy & Astrophysics purpose.


Before you commit, you can re-generate automatically the documentation. You will need sphinx python module for that (sudo apt-get install python-sphinx rst2pdf)

Open a terminal in the repository root directory, type:
> ./dodocs

This script will:

 * move any old documentation found in ./ folder into the folder./docs/old_docs.

 * place the newly generated documentation in the ./ folder under PyAstro_YYYY_MM_DDxhh_mm_ss.pdf name.


If you are lazy and want to create the doc and commit right after, go in the repository root directory, type:
> ./docommit "why this commit is cool"

This script will:

 * ask you if you want to re-generate the documentation

 * recursively delete all .pyc files and all files finishing by ~

 * add all files to the commit

 * commit with the comment "why this commit is cool"