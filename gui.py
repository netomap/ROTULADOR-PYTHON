from tkinter import *
from tkinter import font
from PIL import Image, ImageTk, ImageDraw
import pathlib
import os
from colorama import Fore
import sys
import pandas as pd

class JANELA():

    def __init__(self):
        
        self.imgs_dir = './images/'
        if (not (os.path.exists(self.imgs_dir))):
            print (Fore.RED + f'DIRETÓRIO {self.imgs_dir} NÃO EXISTE!' + Fore.RESET)
            sys.exit(1)
        
        self.annotations_path = 'annotations.csv'
        if (not(os.path.exists(self.annotations_path))):
            with open(self.annotations_path, 'w') as file:
                file.write('img_path,imgw,imgh,ind_classe,xc,yc,w,h')
        
        self.annotations = pd.read_csv('annotations.csv')

        self.win = Tk()
        self.win.resizable(False, False)
        self.win.title('Anotador')
        self.win.geometry('900x600+100+100')

        self.imgs_list = [str(l) for l in list(pathlib.Path(self.imgs_dir).glob('*.jpg'))]
        self.indice_atual = 0

        self.titulo_transicao_imagens = Label(self.win, width=20, height=1, text='Selecionar Imagens', font='Arial 10 bold')
        self.titulo_transicao_imagens.pack()
        self.titulo_transicao_imagens.place(x=600, y=25)

        self.imagem_anterior = Button(self.win, width=5, height=2, command=self.recuar_imagem, text="<<")
        self.imagem_anterior.pack()
        self.imagem_anterior.place(x=600, y=50)

        self.imagem_seguinte = Button(self.win, width=5, height=2, command=self.avancar_imagem, text=">>")
        self.imagem_seguinte.pack()
        self.imagem_seguinte.place(x=800, y=50)

        self.var_imagem_atual = StringVar()
        self.txt_imagem_atual = Label(self.win, width=20, height=2, background='#fff', anchor=NW, textvariable=self.var_imagem_atual)
        self.txt_imagem_atual.pack()
        self.txt_imagem_atual.place(x=650, y=50)

        self.titulo_imagem = Label(self.win, width=30, height=1, text='Imagem selecionada', font='Arial 20 bold')
        self.titulo_imagem.pack()
        self.titulo_imagem.place(x=25, y=25)

        self.canvas = Canvas(self.win, width=500, height=500)
        self.canvas.pack()
        self.atualizar_imagem()
        self.canvas.place(x=25, y=70)

        self.canvas.bind('<Motion>', self.movimento_mouse)
        self.canvas.bind('<Button 1>', self.obter_click)
        self.canvas.bind('<Button 3>', self.resetar_marcacao)
        self.win.bind('<Key>', self.obter_teclado)

        self.ATUALMENTE_ANOTANDO = False
        self.xini = self.xfim = self.yini = self.yfim = self.indice_classe = -1

        self.titulo_transicao_imagens = Label(self.win, width=20, height=1, text='Tipo de Marcação', font='Arial 10 bold')
        self.titulo_transicao_imagens.pack()
        self.titulo_transicao_imagens.place(x=600, y=200)

        self.var_tipo_anotacao = StringVar()
        self.tipo_anotacao = Radiobutton(self.win, text='XcYcWH', value='xcyc', variable=self.var_tipo_anotacao, command=self.selecionar_tipo)
        self.tipo_anotacao.pack()
        self.tipo_anotacao.place(x=600, y=220)
        self.tipo_anotacao.select()

        self.tipo_anotacao = Radiobutton(self.win, text='X1Y1X2Y2', value='x1y1', variable=self.var_tipo_anotacao, command=self.selecionar_tipo)
        self.tipo_anotacao.pack()
        self.tipo_anotacao.place(x=600, y=240)
    
    def selecionar_tipo(self):
        print (f'tipo marcacao: {self.var_tipo_anotacao.get()}')

    def desenhar_retangulo(self):
        if (self.var_tipo_anotacao.get() == 'xcyc'):
            xc, yc = self.xini, self.yini
            w, h = 2*abs(self.xfim-self.xini), 2*abs(self.yfim-self.yini)
            x1, y1, x2, y2 = xc-w/2, yc-h/2, xc+w/2, yc+h/2
        else:
            x1, y1, x2, y2 = self.xini, self.yini, self.xfim, self.yfim
        
        self.img_atual = ImageTk.PhotoImage(self.img_pil_atual.resize((500, 500)))
        self.canvas.create_image(0, 0, image=self.img_atual, anchor=NW)
        self.canvas.create_rectangle(x1, y1, x2, y2, outline='red', width=2)
        self.canvas.create_rectangle(x1, y1-15, x1+30, y1, outline='red', width=2, fill='red')
        self.canvas.create_text(x1+3, y1-10, fill='white', font='Arial 10 bold', text=self.indice_classe)

    def movimento_mouse(self, e):
        if (self.ATUALMENTE_ANOTANDO):
            self.xfim, self.yfim = e.x, e.y
            self.desenhar_retangulo()
    
    def obter_click(self, e):
        if (self.ATUALMENTE_ANOTANDO):
            self.xfim, self.yfim = e.x, e.y
            print (f'anotação realizada!')
            self.salvar_anotacao()
            self.ATUALMENTE_ANOTANDO = False
        else:
            print ('iniciando anotação..')
            self.ATUALMENTE_ANOTANDO = True
            self.xini, self.yini = e.x, e.y

    def salvar_anotacao(self):
        if (self.var_tipo_anotacao.get() == 'xcyc'):
            xc, yc = self.xini, self.yini
            w, h = 2*(abs(self.xfim-self.xini)), 2*(abs(self.yfim-self.yini))
        else:
            x1, y1, x2, y2 = self.xini, self.yini, self.xfim, self.yfim
            w, h = abs(x2-x1), abs(y2-y1)
            xc, yc = min(x1, x2)+w/2, min(y1,y2) + h/2
        
        xc, yc, w, h = xc/self.imgw, yc/self.imgh, w/self.imgw, h/self.imgh

        elemento = {
            'img_path': self.var_imagem_atual.get(),
            'imgw': self.imgw, 'imgh': self.imgh,
            'ind_classe': self.indice_classe,
            'xc': xc, 'yc': yc,
            'w': w, 'h': h
        }
        self.annotations = self.annotations.append(elemento, ignore_index=True)
        self.annotations.to_csv(self.annotations_path, index=False)
        self.atualizar_imagem()

    def resetar_marcacao(self, e):
        self.ATUALMENTE_ANOTANDO = False
        self.xini = self.xfim = self.yini = self.yfim = self.indice_classe = -1

        self.img_atual = ImageTk.PhotoImage(self.img_pil_atual.resize((500, 500)))
        self.canvas.create_image(0, 0, image=self.img_atual, anchor=NW)

    def obter_teclado(self, e):
        self.indice_classe = e.char

    def atualizar_imagem(self):
        self.indice_atual = min(self.indice_atual, len(self.imgs_list)-1)
        self.indice_atual = max(self.indice_atual, 0)
        self.var_imagem_atual.set(self.imgs_list[self.indice_atual])
        self.img_pil_atual = self.desenhar_anotacoes()
        self.imgw, self.imgh = self.img_pil_atual.size
        self.img_atual = ImageTk.PhotoImage(self.img_pil_atual.resize((500, 500)))
        self.canvas.create_image(0, 0, image=self.img_atual, anchor=NW)
    
    def desenhar_anotacoes(self):
        img_path = self.imgs_list[self.indice_atual]
        img_pil = Image.open(img_path).resize((500,500))
        draw = ImageDraw.Draw(img_pil)
        anotacoes = self.annotations[self.annotations['img_path'] == img_path].values
        for img_path,imgw,imgh,ind_classe,xc,yc,w,h in anotacoes:
            x1, y1, x2, y2 = (xc-w/2)*imgw, (yc-h/2)*imgh, (xc+w/2)*imgw, (yc+h/2)*imgh
            draw.rectangle([x1, y1, x2, y2], fill=None, outline='green', width=2)
            draw.rectangle([x1, y1-15,x1+10, y1], fill='green')
            draw.text([x1+3, y1-13], text=str(ind_classe), fill='white')
        
        return img_pil
        
    def avancar_imagem(self):
        self.indice_atual += 1
        self.atualizar_imagem()
    
    def recuar_imagem(self):
        self.indice_atual -= 1
        self.atualizar_imagem()

    def exibir(self):
        self.win.mainloop()

janela = JANELA()
janela.exibir()