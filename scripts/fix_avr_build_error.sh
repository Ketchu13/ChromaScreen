### from klipper issue 4938
# Add the following line to the end of the file

echo "http://deb.debian.org/debian/buster main contrib non-free rpi" >> /etc/apt/sources.list

# Add the following lines to the end of the file
printf "Package: avr-libc avrdude binutils-avr gcc-avr\nPin: release n=buster\nPin-Priority: 1001" > /etc/apt/preferences.d/avr-buster

# Save and exit
sudo apt-get update
sudo apt-get install avr-libc avrdude binutils-avr gcc-avr
cd ~/klipper/ || exit
make clean
# fin
