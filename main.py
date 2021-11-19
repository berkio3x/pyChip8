# -*- coding: utf-8 -*-
import pygame
import sys
import logging
from pygame import draw
from pygame import display


from font import font_data


logging.basicConfig(level=logging.DEBUG)

black= 0 , 0 ,0

class Screen:
    def __init__(self, w=64, h=32):
        self.w = w
        self.h = h
        self.scale = 10
        self.PIXEL_COLOR = 0
        self.PIXEL_ON = (0, 255, 0)
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

        self.FONT_START_ADDRESS = 0x50
        self.FONT_BYTES_COUNT = 80
    
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
                logging.debug('CLEAR SCREEN')
                self.screen.clear_screen()

            if instruction == 0xee:
                pass

            self.pc += 2

        elif opcode == 0x1000:
            '''
            1nnn: Jump to location nnn.
            '''

            addr = ins & 0x0fff
            self.pc = addr
            logging.debug(f' {hex(opcode)} JUMP {hex(addr)}')
            
        
        elif opcode == 0x2000:
            logging.debug('Call addr')
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
            
            reg = (ins & 0x0f00) >> 8
            value = ins & 0x00ff
            val = self.registers[reg]
            self.registers[reg] = val + value 
            logging.debug(f'ADD REG V{reg} {value}')
            self.pc += 2


        elif opcode == 0xA000:
            '''
            Annn: Set I = nnn.
            The value of register I is set to nnn.

            ''' 
            value = ins & 0x0fff
            self.I = value
            self.pc += 2
            logging.debug(f'SET I {hex(value)}')

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


        else:
            input()
            raise Exception(f'{hex(opcode)} not implemented')


if __name__ == "__main__":
    screen = Screen()
    emulator = Emulator(screen=screen)
    #rom = r"C:\Users\KshitijSingh\py\a.ch8"
    rom = r"C:\Users\KshitijSingh\py\pyChip8\ibmlogo.ch8"
    
    emulator.load_rom(font_data)
    emulator.load_rom(rom)
    logging.debug([hex(i) for i in emulator.rom])
    print(len(emulator.rom), "bytes")
    emulator.emulate_cycle()


