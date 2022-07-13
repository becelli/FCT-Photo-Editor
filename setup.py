# Run commands in terminal
import os


copy_lib = 'cp ./modules/libkayn/target/release/liblibkayn.so ./libkayn.so'
rust_build = 'cargo build --release --manifest-path=./modules/libkayn/Cargo.toml'
execute_python = 'python3 ./main.pyw'

def dev():
    os.system(rust_build)
    os.system(copy_lib)
    os.system(execute_python)

def build_executable_win():
    os.system(rust_build)
    os.system(copy_lib)
    #os.system create .exe
if __name__ == '__main__':
    dev()
