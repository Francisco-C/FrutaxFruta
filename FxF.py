import arcade as ac
import pygame
from pygame import mixer

pygame.init()

# icon do jogo

icon = pygame.image.load('game_data/icon.png')
pygame.display.set_icon(icon)

def load_texture_pair(filename):

    return [ac.load_texture(filename), ac.load_texture(filename, mirrored=True)]

############################ VARIAVEIS NECESSÁRIAS PARA O JOGO ############################
largura_ecra = 1000
altura_ecra = 650
titulo = "FRUTA x FRUTA"

player_scale = 1
tile_scale = 1

player_movement_speed = 2
gravidade = 1
player_jump_speed = 8


virado_direita = 0
virado_esquerda = 1

margem_esquerda = 250
margem_direita = 250
margem_baixo = 50
margem_cima = 100

menu = 0
menu_opcoes = 1
comandos = 2
instrucoes = 3
escolher_player = 4
next_lvl = 5
fim = 6
menu_pausa = 7
game_running = 8
###########################################################################################

class PlayerCharacter(ac.Sprite):

    def __init__(self):

        super().__init__()

        # direção inicial do player -> direita
        self.character_face_direction = virado_direita

        # counter para o loop de imagens para animação
        self.run_counter = 0
        self.idle_counter = 0

        self.scale = player_scale

        # estado de salto
        self.jumping = False
        self.player_name = player_name
        # load das imagens para as animações
        self.jump_texture_pair = load_texture_pair(f"game_data/Player/{player_name}/jump.png")
        self.fall_texture_pair = load_texture_pair(f"game_data/Player/{player_name}/fall.png")

        self.inicial = load_texture_pair(f"game_data/Player/{player_name}/idle0.png") # imagem inicial do player
        
        self.idle_texture_pair = [] 
        for i in range(11):
            idle_texture = load_texture_pair(f"game_data/Player/{player_name}/idle{i}.png")
            self.idle_texture_pair.append(idle_texture)

        self.run_textures = []
        for i in range(12):
            run_texture = load_texture_pair(f"game_data/Player/{player_name}/run{i}.png")
            self.run_textures.append(run_texture)

        # definir a imagem inicial do player como estado inicial
        self.texture = self.inicial[0]

        self.set_hit_box(self.texture.hit_box_points)

    def update_animation(self, delta_time: float = 1/60):

        # Verifica se o player está virado para a esquerda ou para a direita
        if self.change_x < 0 and self.character_face_direction == virado_direita:
            self.character_face_direction = virado_esquerda
        elif self.change_x > 0 and self.character_face_direction == virado_esquerda:
            self.character_face_direction = virado_direita

        # animação do player quando está a saltar
        if self.change_y > 0:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        # animação do player quqando está parado
        if self.change_x == 0:
            self.idle_counter += 1
            if self.idle_counter > 10:
                self.idle_counter = 0
            self.texture = self.idle_texture_pair[self.idle_counter][self.character_face_direction]
            return

        # animação do player quando está a correr
        self.run_counter += 1
        if self.run_counter > 11:
            self.run_counter = 0
        self.texture = self.run_textures[self.run_counter][self.character_face_direction]



class TheGame(ac.Window):

    def __init__(self):
        
        #inicia a janela de acordo com os settings
        super().__init__(largura_ecra, altura_ecra, titulo)

        #incia os estados
        self.estado_atual = menu

        #guarda numa lista todos os menus do jogo
        self.menus = []

        texture = ac.load_texture("game_data/Menus/Menu.jpg")
        self.menus.append(texture)

        texture = ac.load_texture("game_data/Menus/menu-opcoes.jpg")
        self.menus.append(texture)

        texture = ac.load_texture("game_data/Menus/commands.jpg")
        self.menus.append(texture)

        texture = ac.load_texture("game_data/Menus/instructions.jpg")
        self.menus.append(texture)

        texture = ac.load_texture("game_data/Menus/caracter.jpg")
        self.menus.append(texture)

        #declaração de todas a sprites do jogo e variaveis necessárias
        self.wall_list = None
        self.player_list = None
        self.back_list = None
        self.fruit_list = None
        self.death_list = None
        self.enemy1_list = None
        self.enemy2_list = None
        self.trampolim_list = None
        self.end_list = None
        self.win_list = None

        self.frutas_countdown = None
        self.nivel = 1
        self.view_bottom = 0
        self.view_left = 0

        self.player_sprite = None

        self.physics_engine = None

        self.paused = None

        self.points = 0

        #cor de fundo do jogo
        ac.set_background_color(ac.csscolor.LIGHT_CYAN)

    def setup(self, nivel):

        self.player_list = ac.SpriteList()
        self.wall_list = ac.SpriteList()
        self.back_list  = ac.SpriteList()
        self.fruit_list = ac.SpriteList()
        self.death_list = ac.SpriteList()
        self.enemy1_list = ac.SpriteList()
        self.enemy2_list = ac.SpriteList()
        self.trampolim_list = ac.SpriteList()
        self.end_list = ac.SpriteList()
        self.win_list = ac.SpriteList()
 
        self.frutas_countdown = 30
        self.view_bottom = 0
        self.view_left = 0
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)
        
        # Nome do mapa de cada nivel
        map_name = f"game_data/Mapas/nivel{self.nivel}.tmx"
       
        # Nome de cada layer nos mapas
        walls_layer_name = 'walls'
        background_layer_name = 'background'
        fruit_layer_name = 'fruta'
        death_layer_name = 'death'
        enemy1_layer_name = "inimigo1"
        enemy2_layer_name = "inimigo2"
        trampolim_layer_name = "trampolim"
        end_layer_name = "next"
        win_layer_name = "end"

        # leitura do mapa
        mapa = ac.tilemap.read_tmx(map_name)
        
        # guarda cada categoria de sprites diferentes do mapa numa lista
        self.wall_list = ac.tilemap.process_layer(map_object=mapa, layer_name=walls_layer_name, scaling=tile_scale)
    
        self.back_list = ac.tilemap.process_layer(mapa,background_layer_name, tile_scale)
        self.fruit_list = ac.tilemap.process_layer(mapa, fruit_layer_name, tile_scale)
        self.death_list = ac.tilemap.process_layer(mapa, death_layer_name, tile_scale)
        self.enemy1_list = ac.tilemap.process_layer(mapa, enemy1_layer_name, tile_scale)
        self.enemy2_list = ac.tilemap.process_layer(mapa, enemy2_layer_name, tile_scale)
        
        # movimento dos enimigos
        for enemy in self.enemy1_list:
            enemy.change_x = -2

        for enemy in self.enemy2_list:
            enemy.change_y = 2

        self.trampolim_list = ac.tilemap.process_layer(mapa, trampolim_layer_name, tile_scale)
        self.end_list = ac.tilemap.process_layer(mapa, end_layer_name, tile_scale)
        self.win_list = ac.tilemap.process_layer(mapa, win_layer_name, tile_scale)
            
        # cor de fundo
        if mapa.background_color:
            ac.set_background_color(mapa.background_color)

        # criação do engenho que dá a física do player    
        self.physics_engine = ac.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, gravidade)
        
        # musica de fundo
        mixer.music.load('game_data/Sounds/music.wav')
        mixer.music.play(-1)
        mixer.music.set_volume(0.1)
        
    def draw_menus(self, estado):

        # desenho de cada menu inicial dependendo do estado
        menu_texture = self.menus[estado]
        ac.draw_texture_rectangle(largura_ecra//2, altura_ecra//2, menu_texture.width, menu_texture.height, menu_texture,0)       

    def draw_pause_screen(self):
        
        # desenho do menu de pausa se estiver no estado correspondente
        pausa_texture = ac.load_texture('game_data/Menus/PAUSA.jpg')
        pausa_texture.draw_scaled(x_center,y_center)

    def draw_next_screen(self):

        #desenho do menu de nivel seguinte se estiver no estado correspondente
        next_texture = ac.load_texture('game_data/Menus/NEXTLVL.jpg')
        next_texture.draw_scaled(x_center,y_center)
        
    def draw_win_screen(self):

        # desenho do menu de vitória se estiver no estado correspondente
        win_texture = ac.load_texture('game_data/Menus/END.jpg')
        win_texture.draw_scaled(x_center,y_center)
        points_text = f'{self.points}'
        ac.draw_text(points_text, 520, 80, ac.csscolor.BLACK ,60)

    def on_draw(self):
        # render do ecra

        ac.start_render()

        # verifica em qual estado estamos e prossegue com a função correspondente
        if self.estado_atual == menu:
            self.draw_menus(menu)

        elif self.estado_atual == menu_opcoes:
            self.draw_menus(menu_opcoes)

        elif self.estado_atual == comandos:
            self.draw_menus(comandos)

        elif self.estado_atual == instrucoes:
            self.draw_menus(instrucoes)
        
        elif self.estado_atual == escolher_player:
            self.draw_menus(escolher_player)

        elif self.estado_atual == game_running:

            self.back_list.draw()
            self.wall_list.draw()
            self.enemy1_list.draw()
            self.enemy2_list.draw()
            self.end_list.draw()
            self.trampolim_list.draw()
            self.fruit_list.draw()
            self.death_list.draw()
            self.win_list.draw()
            self.player_list.draw()

            score_text = f"Fruits left: {self.frutas_countdown}"
            ac.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom, ac.csscolor.BLACK, 18)

        elif self.estado_atual == menu_pausa:
            self.draw_pause_screen()

        elif self.estado_atual == next_lvl:
            self.draw_next_screen()

        elif self.estado_atual == fim:
            self.draw_win_screen()

    def on_key_press(self, key, modifiers):
        
        # verifição de qual estado o jogo se encontra e declaração de quais teclas podemos usar no determinado estado
        global player_name
        
        if self.estado_atual == menu:
            if key == ac.key.X:
                self.estado_atual = menu_opcoes

        elif self.estado_atual == menu_opcoes:
            if key == ac.key.X:
                self.estado_atual = instrucoes
            elif key == ac.key.C:
                self.estado_atual = comandos

        elif self.estado_atual == comandos:
            if key == ac.key.X:
                self.estado_atual = instrucoes

        elif self.estado_atual == instrucoes:
            if key == ac.key.X:
                self.estado_atual = escolher_player

        elif self.estado_atual == escolher_player:
            if key == ac.key.KEY_1 or key == ac.key.NUM_1:
                player_name = 'BlueGuy'
                self.setup(self.nivel)
                self.estado_atual = game_running
            elif key == ac.key.KEY_2 or key == ac.key.NUM_2:
                player_name = 'MiRmO'
                self.setup(self.nivel)
                self.estado_atual = game_running
            elif key == ac.key.KEY_3 or key == ac.key.NUM_3:
                player_name = 'Frog'
                self.setup(self.nivel)
                self.estado_atual = game_running
            elif key == ac.key.KEY_4 or key == ac.key.NUM_4:
                player_name = 'Indio'
                self.setup(self.nivel)
                self.estado_atual = game_running
        
        elif self.estado_atual == game_running:

            # se o player colidir com um trampolim o salto aumenta
            if ac.check_for_collision_with_list(self.player_sprite, self.trampolim_list):
                self.player_jump_speed = 11
            else:
                self.player_jump_speed = player_jump_speed    

            # salto
            if key == ac.key.UP or key == ac.key.W:            
                if self.physics_engine.can_jump():                
                    self.player_sprite.change_y = self.player_jump_speed
            
            # andar para a esquerda e direita
            elif key == ac.key.LEFT or key == ac.key.A:
                self.player_sprite.change_x = -player_movement_speed
            elif key == ac.key.RIGHT or key == ac.key.D:
                self.player_sprite.change_x = player_movement_speed

            # pausa
            elif key == ac.key.ESCAPE:
                self.paused = not self.paused
                self.estado_atual = menu_pausa
        
        elif self.estado_atual == menu_pausa:
            if key == ac.key.ESCAPE:
                self.paused = not self.paused
                self.estado_atual = game_running
        
        elif self.estado_atual == next_lvl:
            if key == ac.key.X:
                self.estado_atual = game_running

        
    def on_key_release(self, key, modifiers):

        # se o utilizador parar de primir a tecla o player para de andar
        if key == ac.key.LEFT or key == ac.key.A:
            self.player_sprite.change_x = 0
        elif key == ac.key.RIGHT or key == ac.key.D:
            self.player_sprite.change_x = 0
        
    
    def on_update(self, delta_time):
        
        # função que dá constante updates quando o jogo se encontra a correr, estado de game_running

        self.set_update_rate(1/20) # FP's do jogo(frame rates)
        
        # pausa e resume o jogo
        if self.paused:
            return


        if self.estado_atual == game_running:
            
            # update da sprite do player e das suas animações
            self.player_list.update()
            self.player_list.update_animation()
            
            # update do física do player
            self.physics_engine.update()
        
            # verifica que o player colide com uma fruta
            hit_fruta = ac.check_for_collision_with_list(self.player_sprite, self.fruit_list)

            # loop para cada fruta em que o player colide e remove a do mapa diminui a o score necessário para o score final
            for fruta in hit_fruta:

                fruta.remove_from_sprite_lists()
                Fsound = mixer.Sound('game_data/Sounds/fruit_sound.wav')
                Fsound.play()
                Fsound.set_volume(0.1)
                self.frutas_countdown -= 1

            # verifica se o player colide com algum objeto que o faça perder retorna o player para o inicia do nivel
            if ac.check_for_collision_with_list(self.player_sprite, self.death_list) or ac.check_for_collision_with_list(self.player_sprite, self.enemy1_list) or ac.check_for_collision_with_list(self.player_sprite, self.enemy2_list):
                
                Lsound = mixer.Sound('game_data/Sounds/lose_sound.wav')
                Lsound.play()
                Lsound.set_volume(0.1)

                self.player_sprite.change_x = 0
                self.player_sprite.change_y = 0
                self.player_sprite.center_x = 50
                self.player_sprite.center_y = 50
            
            # update dos movimentos dos inimigos, se bater contra um obstaculo o movimento muda de direção
            self.enemy1_list.update()
            self.enemy2_list.update()
            
            for enemy in self.enemy1_list:
                if ac.check_for_collision_with_list(enemy, self.wall_list):
                        enemy.change_x *= -1

            for enemy in self.enemy2_list:
                if ac.check_for_collision_with_list(enemy, self.wall_list):
                        enemy.change_y *= -1
            
            # criação de uma 'câmara' para acompanhar o player ao longo dos mapas
            changed = False
            # câmara que acompanha para a esquerda
            left_boundary = self.view_left + margem_esquerda
            if self.player_sprite.left < left_boundary:
                self.view_left -= left_boundary - self.player_sprite.left
                changed = True

            # câmara que acompanha para a direita
            right_boundary = self.view_left + largura_ecra - margem_direita
            if self.player_sprite.right > right_boundary:
                self.view_left += self.player_sprite.right - right_boundary
                changed = True


            global x_center
            x_center = largura_ecra//2 +self.view_left

            # câmara que acompanha para a cima
            top_boundary = self.view_bottom + altura_ecra - margem_cima
            if self.player_sprite.top > top_boundary:
                self.view_bottom += self.player_sprite.top - top_boundary
                changed = True

            # câmara que acompanha para a baixo
            bottom_boundary = self.view_bottom + margem_baixo
            if self.player_sprite.bottom < bottom_boundary:
                self.view_bottom -= bottom_boundary - self.player_sprite.bottom
                changed = True


            global y_center
            y_center = altura_ecra//2 + self.view_bottom

            if changed:
                # apenas movimenta com inteiros para não ficarem pixeis desalinhados
                self.view_bottom = int(self.view_bottom)
                self.view_left = int(self.view_left)

                # faz o movimento da câmara
                ac.set_viewport(self.view_left, largura_ecra + self.view_left, self.view_bottom, altura_ecra + self.view_bottom)

           # se o player colidir com o final do nivel muda para o menu e carrega o próximo nivel
           
            if ac.check_for_collision_with_list(self.player_sprite, self.end_list):
                self.estado_atual = next_lvl
                self.nivel += 1

                if self.frutas_countdown == 0:
                    self.points += 1

                self.setup(self.nivel)

                self.view_left = 0
                self.view_bottom = 0
                changed = True

            # se o player concluir o ultimo nivel aparece o menu final com a pontuação
            
            if ac.check_for_collision_with_list(self.player_sprite, self.win_list):
                
                if self.frutas_countdown == 0:
                    self.points += 1

                self.estado_atual = fim

def main():

    # funçáo que inicia de facto o jogo e todas as suas componentes

    window = TheGame()
    window.on_draw()
    ac.run()

if __name__ == "__main__":
    main()