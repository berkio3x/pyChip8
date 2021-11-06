# -*- coding: utf-8 -*-
import pygame
import sys
import logging
from pygame import draw
from pygame import display

logging.basicConfig(level=logging.DEBUG)

black= 0 , 0 ,0


class Screen:
    def __init__(self, w=64, h=32):
        self.w = w
        self.h = h
        self.scale = 10
        self.PIXEL_COLOR = 0
        self.PIXEL_ON = (255, 255, 255)
        self.PIXEL_OFF = (0,0,0)
        pygame.init()
        self.screen = pygame.display.set_mode((self.w * self.scale, self.h * self.scale))
        self.screen.fill('darkgreen')
        display.flip()
        display.set_caption('Chip8 emulator - pyChip8')

    def get_pixel_value(self, x, y):
        pixel_color = self.screen.get_at((x * self.scale, y * self.scale))
        
        color = 0

        if pixel_color == self.PIXEL_ON:
            color = 1

        if color:
            self.PIXEL_COLOR = self.PIXEL_ON
        else:
            self.PIXEL_COLOR = self.PIXEL_OFF

        return color

    def set_pixel(self, x, y):
        draw.rect(
                self.screen,
                self.PIXEL_COLOR,
                (x*self.scale, y*self.scale, self.scale, self.scale))

    def clear(self):
        pass



class Emulator:
    def __init__(self, screen=Screen()):
        
        self.screen = screen
        self.registers = [0]*16
        self.I = 0
        self.memory = 4096 * [0x0]
        self.pc = 0
        self.DRAW_FLAG = False
        self.display = [0]*64*32
    

    def load_rom(self,path):
        rom =  []
        with open(path,"rb") as f:
            logging.debug(f)
            _file =  f.read()
            #logging.debug(_file)

            for i in _file:
                rom.append(i)

        self.rom = rom
        logging.debug(self.rom)

        # print(type(self.rom[1]),",,,")


    def emulate_cycle(self):
        while True and self.pc < len(self.rom):
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()


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
            display.flip()


    def execute(self, ins):

        opcode = ins & 0xf000

        if opcode == 0x00:
            instruction = ins & 0x0fff

            if instruction == 0xe0:
                logging.debug('clear screen()')
            if instruction == 0xee:
                pass

            self.pc += 2

        elif opcode == 0x1000:
            addr = opcode & 0x0fff
            self.pc = addr
            logging.debug('jump')
        
        elif opcode == 0x2000:
            logging.debug('Call addr')
            self.pc += 2
        
        elif opcode == 0x6000:
            '''
            6XNN LD Vx NN
            '''
            logging.debug('set register value')
            reg = ins & 0xf00 >> 7
            value = ins & 0xff
            print(reg,"reeeeh", self.registers)
            self.registers[reg] = value
            self.pc += 2
        
        elif opcode == 0x7000:
            logging.debug('add register value')
            reg = ins & 0xf00 >> 7
            value = ins & 0xff
            val = self.registers[reg]
            self.registers[reg] = val + value 
            self.pc += 2


        elif opcode == 0xA000:
            logging.debug('set index register')
            value = opcode & 0x0fff
            self.I = value
            self.pc += 2

        elif opcode == 0xd000:
            '''
            Dxyn - draw Vx, Vy, nibble
            Display n-byte sprite starting at memory location I at (Vx, Vy), set VF= collision.
            '''
            
            logging.debug('draw')
            
            width = 8
            height = ins & 0x000f
            
            x = self.registers[ (ins & 0x0f00) >> 8];
            y = self.registers[ (ins & 0x00f0) >> 4];
            
            self.registers[0xf] = 0

            for yline in range(0, height):
                pixel = self.rom[self.I + yline]

                for xline in range(8):
                    if (pixel & (0x80 >> xline)) != 0:
                        
                        #if self.screen.data[ (x + xline + ((y+yline) * 64))]  == 1:
                        #    self.registers[0xf]=1

                        pixel_value = self.screen.get_pixel_value(x,y)
                        pixel_value ^= 1
                        self.screen.set_pixel(x+xline, y+yline)

            self.darw_flag = True 
            self.pc += 2


        else:
            logging.debug(f'{hex(opcode)} not implemented')
            self.pc += 2

if __name__ == "__main__":
    screen = Screen()
    emulator = Emulator(screen=screen)
    #rom = r"C:\Users\KshitijSingh\py\a.ch8"
    rom = r"C:\Users\KshitijSingh\py\ibmlogo.ch8"
    
    emulator.load_rom(rom)

    emulator.emulate_cycle()


