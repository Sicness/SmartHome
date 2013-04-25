CC=gcc

gpio_11:
	$(CC) -o gpio_11 gpio_11.c -l bcm2835

install:
	sudo cp gpio_11 /usr/local/bin/
	sudo chown root /usr/local/bin/gpio_11
	sudo chmod +s /usr/local/bin/gpio_11

unistall:
	sudo rm /usr/local/bin/gpio_11

clean:
	rm gpio11
