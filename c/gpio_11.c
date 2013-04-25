// blink.c
//
// After installing bcm2835, you can build this 
// with something like:
// gcc -o blink blink.c -l bcm2835
// sudo ./blink
//
// Forked from:
//  Author: Mike McCauley
//  Copyright (C) 2011 Mike McCauley
//  $Id: RF22.h,v 1.21 2012/05/30 01:51:25 mikem Exp $

#include <bcm2835.h>
#include <stdio.h>

// Blinks on RPi Plug P1 pin 11 (which is GPIO pin 17)
#define PIN RPI_GPIO_P1_11

int main(int argc, char **argv)
{
		if (argc == 1)
			return printf("Use %s <1/0>\n", argv[0]);

		uint8_t state = 42;		// :D Sorry
		if (argv[1][0] == '1')
			state = 1;
		if (argv[1][0] == '0')
			state = 0;
		if (state == 42)
			return printf("Use %s <1/0>\n");

    if (!bcm2835_init())
			return 1;

    // Set the pin to be an output
    bcm2835_gpio_fsel(PIN, BCM2835_GPIO_FSEL_OUTP);

		if (state)
			bcm2835_gpio_write(PIN, HIGH);
		else
			bcm2835_gpio_write(PIN, LOW);

    bcm2835_close();
    return 0;
}

