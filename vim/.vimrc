set nocompatible

let mapleader = " "
inoremap jj <Esc>

syntax on

set showmode

set hlsearch
set incsearch
set ignorecase
set showmatch
map <leader>l :noh<cr>

filetype plugin indent on
" show existing tab with 4 spaces width
set tabstop=4
" when indenting with '>', use 4 spaces width
set shiftwidth=4
" On pressing tab, insert 4 spaces
set expandtab
