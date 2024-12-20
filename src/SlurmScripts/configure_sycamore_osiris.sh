#!/bin/bash
#SBATCH --job-name=configure_osiris
#SBATCH --qos=short
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=1-0
#SBATCH --output=configure_osiris%j.out

# ============================================
#  the configure/ directory must contain the
#    nprint-1.2.1.tar.gz tarball, it is included in the repo
#
#  all software (libpcap, tcpdump, nprint) will be installed to the
#    local user's home directory under: $HOME/.local/
#
#  cd into SlurmScripts/ and run `sbatch configure_sycamore_osiris.sh`, log
#    file will be in the same directory to diagnose issues
# ============================================

install_libpcap() {
    echo "=============installing libpcap locally============="
    wget https://www.tcpdump.org/release/libpcap-1.10.4.tar.gz
    tar -xvf libpcap-1.10.4.tar.gz
    cd libpcap-1.10.4 || exit

    # install to local directory
    ./configure --prefix=$HOME/.local
    make
    make install
    cd ..
    rm -rf libpcap-1.10.4 libpcap-1.10.4.tar.gz
    echo "=============libpcap installed locally============="
}

install_nprint() {
    echo "=============installing nprint============="
    cd /home/"$USER"/osirisml/OsirisML/configure || exit
    tar -xvf nprint-1.2.1.tar.gz
    cd nprint-1.2.1 || exit

    # install to local directory with local libpcap
    ./configure --prefix=$HOME/.local CPPFLAGS="-I$HOME/.local/include" LDFLAGS="-L$HOME/.local/lib"
    make
    make install
    cd ..
    rm -rf nprint-1.2.1
    echo "=============nprint installed locally============="
}

install_tcpdump() {
    echo "=============installing tcpdump locally============="
    wget https://www.tcpdump.org/release/tcpdump-4.99.4.tar.gz
    tar -xvf tcpdump-4.99.4.tar.gz
    cd tcpdump-4.99.4 || exit

    # install to local directory with local libpcap
    ./configure --prefix=$HOME/.local CPPFLAGS="-I$HOME/.local/include" LDFLAGS="-L$HOME/.local/lib"
    make
    make install
    cd ..
    rm -rf tcpdump-4.99.4 tcpdump-4.99.4.tar.gz
    echo "=============tcpdump installed locally============="
}

update_library_paths() {
    echo "=============updating library paths============="
    export PATH="$HOME/.local/bin:$PATH"
    export LD_LIBRARY_PATH="$HOME/.local/lib:$LD_LIBRARY_PATH"

    # add the exports to shell for persistence
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    fi

    if ! grep -q 'export LD_LIBRARY_PATH="$HOME/.local/lib:$LD_LIBRARY_PATH"' ~/.bashrc; then
        echo 'export LD_LIBRARY_PATH="$HOME/.local/lib:$LD_LIBRARY_PATH"' >> ~/.bashrc
    fi

    source ~/.bashrc
    echo "=============library paths updated============="
}

install_python_dependencies() {
    echo "=============installing python dependencies============="
    pip install --user pandas scikit-learn xgboost scapy
    echo "=============python dependencies installed============="
}

main() {
    install_libpcap
    install_nprint
    install_tcpdump
    update_library_paths
    install_python_dependencies

    echo "=============Configuration script completed successfully!!!!!! yahoo============="
    echo "=============try running nprint --version and tcpdump --version to make sure they're installed correctly============="

}

main
