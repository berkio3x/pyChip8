# -*- coding: utf-8 -*-
import pygame
import sys
import logging
from pygame import draw
from pygame import display
from timers import DelayTimer

import random
from font import font_data


logging.basicConfig(level=logging.DEBUG)

black= 0 , 0 ,0

class Screen:
    def __init__(self, w=64, h=32):
        self.w = w
        self.h = h
        self.scale = 10
        self.PIXEL_COLOR = 0
        self.PIXEL_ON = (90, 255, 255)
        self.PIXEL_OFF = (0,0,0)
        pygame.init()
        self.screen = pygame.display.set_mode((self.w * self.scale, self.h * self.scale))
        self.screen.fill('black')
        display.flip()
        display.set_caption('Chip8 emulator - pyChip8')

    def get_pixel_value(self, x, y):
        pixel_color = self.screen.get_at((x * self.scale, y * self.scale))
        
        color = 0

        if pixel_color == self.PIXEL_ON:
            color = 1

        return color

    def set_pixel(self, x, y, color):

        if color:
            pixel_color = self.PIXEL_ON
        else:
            pixel_color = self.PIXEL_OFF

        #logging.debug(f'setting pixel color to: {pixel_color}')

        draw.rect(
                self.screen,
                pixel_color,
                (x*self.scale, y*self.scale, self.scale, self.scale))

    def clear_screen(self):
        self.screen.fill('black')



class Emulator:
    def __init__(self, screen=Screen()):
        
        self.screen = screen
        self.registers = [0]*16
        self.I = 0
        self.memory = 4096 * [0x0]
        self.pc = 0x200
        self.DRAW_FLAG = False
        self.display = [0]*64*32
        self.rom = [0x0] * 4096
        self.delay_timer = DelayTimer(0)
        self.sp = 0
        self.stack = [0 for _ in range(16)]

        self.FONT_START_ADDRESS = 0x50
        self.FONT_BYTES_COUNT = 80


        pygame.time.set_timer(pygame.USEREVENT+1, int(1000 / 60))




    
    def load_rom(self, path):
        rom =  []
        if isinstance(path, list):
            for index, byte in enumerate(path):
                self.rom[self.FONT_START_ADDRESS + index] = byte
        else:
            with open(path,"rb") as f:
                logging.debug(f)
                _file =  f.read()
                #logging.debug(_file)

                for index, byte in enumerate(_file):
                    self.rom[0x200 + index] = byte


        # print(type(self.rom[1]),",,,")


    def emulate_cycle(self):
        while True and self.pc < len(self.rom):
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()

                if event.type == pygame.USEREVENT+1:
                    self.delay_timer.countdown()


            ''' Each instruction is two bytes.
            first shift the high byte to left 8 bits , i.e add 8 zeros
            then do a bitwise or with low byte to get the final instruction.

            '''

            h_b  = self.rom[self.pc]
            l_b = self.rom[self.pc + 1]

            opcode =  h_b << 8 | l_b

            #self.decode()
            if self.DRAW_FLAG:
                pass


            self.execute(opcode)
            # input("next?")
            display.flip()


    def execute(self, ins):

        opcode = ins & 0xf000

        if opcode == 0xA000:

            '''
            Annn: Set I = nnn.
            The value of register I is set to nnn.

            ''' 
            # value = ins & 0x0fff
            # self.I = value
            # self.pc += 2
            # logging.debug(f'SET I {hex(value)}')

            nnn = (ins & 0x0fff)
            logging.debug(f'SET {self.I} {nnn}')

            self.I = nnn
            self.pc += 2



        elif opcode == 0xd000:
            '''
            Dxyn - draw Vx, Vy, nibble
            Display n-byte sprite starting at memory location I at (Vx, Vy), set VF= collision.
            '''
            
            width = 8
            height = ins & 0x000f
            reg_x =  (ins & 0x0f00) >> 8
            reg_y =  (ins & 0x00f0) >> 4
            x = self.registers[reg_x];
            y = self.registers[reg_y];
            
            logging.debug(f'DRAW V{reg_x} V{reg_y} {height}')
            
            self.registers[0xf] = 0

            for yline in range(0, height):
                pixel = self.rom[self.I + yline]
                for xline in range(8):
                    if (pixel & (0x80 >> xline)) != 0:
                        pixel_value = self.screen.get_pixel_value(x+xline,y+yline)
                        pixel_value ^= 1
                        self.screen.set_pixel(x+xline, y+yline, pixel_value)
                        if pixel_value == 0:
                            self.registers[0xf] = 1
                        else:
                            self.registers[0xf] = 0

            self.pc += 2


        # --
        elif opcode == 0xc000:
            reg = (ins & 0x0f00) >> 8
            value = ins & 0x00ff
            rand = random.randint(0,255)
            self.registers[reg] = rand & value 

            logging.debug(f'SET V{reg} {rand} AND {value}')
            self.pc += 2



        elif opcode == 0x8000:
            x = (ins & 0x0f00) >> 8
            y = (ins & 0x00f0) >> 4

            Vx = self.registers[x]
            Vy = self.registers[y]

            end = ins & 0x000f

            if end == 0x0:
                # input()
                self.registers[x] = Vy
            if end == 0x1:
                self.registers[x] =  Vx | Vy 
            if end == 0x2:
                self.registers[x] =  Vx & Vy 
            if end == 0x3:
                self.registers[x] =  Vx ^ Vy 

            if end == 0x4:
                val = Vx + Vy 
                if val > 0xff:
                    self.registers[0xf] = 1
                else:
                    self.registers[0xf] = 0

                self.registers[x] = (val & 0x00ff)

            if end == 0x5:
                if Vx > Vy:
                    self.registers[0xf] = 1
                else:
                    self.registers[0xf] = 0

                self.registers[x] = (Vx - Vy) & 0xff

                
            if end == 0x6:
                # input(">>")
                if (Vx & 0x1) == 1:
                    self.registers[0xf] = 1
                else:
                    self.registers[0xf] = 0 
                self.registers[x] = (self.registers[x] >> 1) # divide  by 2 or right shift by one bit

            if end == 0x7:
                if Vy > Vx:
                    self.registers[0xf] = 1
                else:
                    self.registers[0xf] = 0 
                self.registers[x] = (Vy - Vx) &0xff

            if end == 0xe:
                if (Vx & 0xf000) == 1:
                    self.registers[0xf] = 1
                else:
                    self.registers[0xf] = 0
                self.registers[x] *= 2
            self.pc += 2


        elif opcode == 0x00:
            instruction = ins & 0x0fff

            if instruction == 0xe0:
                logging.debug('CLEAR SCREEN')
                self.screen.clear_screen()

            if instruction == 0xee:
                pass
                self.pc = self.stack[self.sp]
                self.sp -= 1

            self.pc += 2

        elif opcode == 0x1000:
            '''
            1nnn: Jump to location nnn.
            '''

            addr = ins & 0x0fff
            self.pc = addr
            # logging.debug(f' {hex(opcode)} JUMP {hex(addr)}')
            
        
        elif opcode == 0x2000:
            pass
            # self.pc += 2
            nnn = (ins & 0x0fff)

            self.sp += 1
            self.stack[self.sp] = self.pc
            self.pc = nnn

            logging.debug(f'Jump to addr -> {nnn}')
            logging.debug(f'opcode @addr <{nnn}> {self.rom[self.pc]}')


        elif opcode == 0x3000:
            x = (ins & 0x0f00) >> 8 
            kk = (ins & 0x00ff)
            if self.registers[x] == kk:
                self.pc += 4 # skip next instruction
            else:
                self.pc += 2

        elif opcode == 0x4000:
            x = (ins & 0x0f00) >> 8
            kk = (ins & 0x00ff)
            if self.registers[x] != kk:
                self.pc += 4 
            else:
                self.pc += 2

        elif opcode == 0x5000:
            x = (ins & 0x0f00) >> 8
            y = (ins & 0x00f0) >> 4

            Vx = self.registers[x]
            Vy = self.registers[y]

            if Vx == Vy:
                self.pc += 4
            else:
                self.pc += 2

        elif opcode == 0x6000:
            '''
            6XNN LD Vx NN : Load value NN into register Vx
            '''
            
            reg = (ins & 0x0f00) >> 8
            value = ins & 0x00ff 
            self.registers[reg] = value
            self.pc += 2
            logging.debug(f'LOAD  V{reg} {value}')
       

        elif opcode == 0x7000:
            
            x = (ins & 0x0f00) >> 8
            kk = ins & 0x00ff
            
            logging.debug(self.registers)
            self.registers[x] =  (self.registers[x] + kk) & 0xff 
            self.pc += 2

            

            logging.debug(f'{x} : {kk}')
            logging.debug(self.registers)



        elif opcode == 0x9000:

            # import pdb;pdb.set_trace()

            x = (ins & 0x0f00) >> 8
            y = (ins & 0x00f0) >> 4

            Vx = self.registers[x]
            Vy = self.registers[y]

            logging.debug(self.registers)
            logging.debug(f'{x} {y}')

            if Vx != Vy:
                self.pc += 4
            else:
                self.pc += 2

        elif opcode == 0xf000:
            x = (ins & 0x0f00) >> 8

            low_bytes = (ins & 0x00ff)


            if low_bytes == 0x07:
                self.registers[x] = self.delay_timer.get_time()

            if low_bytes == 0x0a:
                self.registers[x] = input()

            if low_bytes == 0x15:
                self.delay_timer.set_time(
                    self.registers[x]
                    )

            if low_bytes == 0x65:
                for i in range(x+1):
                    self.registers[i] = self.rom[self.I+i]

            if low_bytes == 0x55:
                for i in range(x+1):
                    self.rom[self.I+i] = self.registers[i]

            self.pc += 2

        else:
            input()
            raise Exception(f'{hex(opcode)} not implemented')


if __name__ == "__main__":
    screen = Screen()
    emulator = Emulator(screen=screen)
    #rom = r"C:\Users\KshitijSingh\py\a.ch8"
    # rom = r"/Users/akshaymahurkar/Documents/progs/pyChip8/ibmlogo.ch8"
    # rom = r"/Users/akshaymahurkar/Downloads/LANDING"
    rom = r"/Users/akshaymahurkar/Downloads/test_opcode.ch8"
    # rom = r"/Users/akshaymahurkar/Downloads/chiptest.ch8"
    # rom = r"/Users/akshaymahurkar/Downloads/c8_test.c8")
    # rom = r"/Users/akshaymahurkar/Downloads/redOctober.ch8"
    
    emulator.load_rom(font_data)
    emulator.load_rom(rom)
    logging.debug([hex(i) for i in emulator.rom])
    print(len(emulator.rom), "bytes")
    emulator.emulate_cycle()


