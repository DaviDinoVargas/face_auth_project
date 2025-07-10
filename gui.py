import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import threading
import time
import json
from face_recognition import FaceRecognition
from data_manager import DataManager
from styles import create_button, create_label, create_text, create_frame, create_canvas, configure_styles

class FaceAuthApp:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.current_user = None
        self.currently_registering = False
        self.frame_buffer = None
        self.canvas_image = None
        
        self.face_recognition = FaceRecognition(self)
        self.data_manager = DataManager()
        
        self.root.bind("<<NewFrame>>", lambda e: self.safe_canvas_update())
        self.create_gui()

    def create_gui(self):
        self.root.title("Face Auth Pro Max Detector From Dino")
        self.root.geometry("450x650")
        self.root.resizable(False, False)
        
        configure_styles()

        # Main Frame
        self.main_frame = create_frame(self.root)
        self.main_frame.pack_propagate(False)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        header = create_frame(self.main_frame)
        header.pack(fill=tk.X, pady=(0, 20))
        
        logo = create_label(header, "Face Auth Pro Max Detector From Dino", font=("Segoe UI Semibold", 16))
        logo.pack(expand=True)

        # Main Buttons
        btn_register = create_button(self.main_frame, "🆕 Cadastrar Usuário", self.start_face_mesh)
        btn_register.pack(fill=tk.X, pady=5)

        btn_view = create_button(self.main_frame, "👥 Visualizar Usuários", self.view_users)
        btn_view.pack(fill=tk.X, pady=5)

        btn_enter = create_button(self.main_frame, "🔑 Entrar no Sistema", self.enter_application)
        btn_enter.pack(fill=tk.X, pady=5)

        # Camera Frame
        self.mesh_frame = create_frame(self.root, style="Auth.TFrame")
        self.canvas = create_canvas(self.mesh_frame, width=400, height=300)
        self.canvas.pack(pady=20)
        btn_save = create_button(self.mesh_frame, "Salvar Amostra", self.save_landmarks)
        btn_save.pack(pady=10)
        btn_back = create_button(self.mesh_frame, "Voltar", self.stop_face_mesh)
        btn_back.pack(pady=10)

        # View Frame
        self.view_frame = create_frame(self.root)
        
        # Auth Frame
        self.auth_frame = create_frame(self.root)
        btn_authenticate = create_button(self.auth_frame, "Autenticar", self.authenticate)
        btn_authenticate.pack(pady=10)
        btn_back_auth = create_button(self.auth_frame, "Voltar", self.stop_face_mesh)
        btn_back_auth.pack(pady=10)

        # Authenticated Frame
        self.authenticated_frame = create_frame(self.root, style="Auth.TFrame")
        self.lbl_success = create_label(self.authenticated_frame, "", 
                                      font=("Segoe UI Semibold", 16), 
                                      foreground="#4CAF50")
        self.lbl_success.pack(pady=40)
        btn_back_auth_success = create_button(self.authenticated_frame, "Voltar", self.switch_to_main)
        btn_back_auth_success.pack(pady=10)

    def view_users(self):
        self.clear_frame(self.view_frame)
        
        # Top Bar com Botão Voltar e Pesquisa
        top_bar = create_frame(self.view_frame)
        top_bar.pack(fill=tk.X, pady=5)
        
        # Botão Voltar
        create_button(top_bar, "← Voltar", self.switch_to_main, width=10).pack(side=tk.LEFT, padx=10)
        
        # Barra de Pesquisa
        search_frame = create_frame(top_bar)
        search_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            width=25
        )
        search_entry.pack(side=tk.RIGHT, padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self._populate_users_search())
        create_label(search_frame, "🔍 Pesquisar:", font=("Segoe UI", 10)).pack(side=tk.RIGHT)

        # Container com scroll
        container = create_frame(self.view_frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Configuração do canvas e scrollbar
        canvas = create_canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = create_frame(canvas)
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
    # Configuração do scroll
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))  # <--- Corrigido
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")  # <--- Corrigido
        canvas.configure(yscrollcommand=scrollbar.set)

        # Na chamada do populate_users:
        self.root.after(100, lambda: self._populate_users(self.scrollable_frame))

        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Carregamento assíncrono
        self.root.after(100, lambda: self._populate_users(self.scrollable_frame))


    def _populate_users_search(self):
        query = self.search_var.get().lower()
        
        # Filtra usuários
        filtered_users = []
        for user in self.data_manager.users_data:
            if (query in user['username'].lower() or 
                query in str(user['id']).zfill(6) or 
                query in user['filename'].lower()):
                filtered_users.append(user)
        
        # Limpa APENAS a área scrollável
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Popula com os resultados filtrados
        self._populate_users(self.scrollable_frame, filtered_users)

    def _populate_users(self, parent, users=None):
        # Limpa todos os widgets existentes no frame pai
        for widget in parent.winfo_children():
            widget.destroy()
        
        users = users if users else self.data_manager.users_data
        
        for user in users:
            user_frame = create_frame(parent)
            user_frame.pack(fill=tk.X, expand=True, pady=3)

            lbl_text = f"{user['username']} (ID: {user['id']:06d})"
            lbl = create_label(user_frame, lbl_text, width=25, anchor="w")
            lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

            btn_frame = create_frame(user_frame)
            btn_frame.pack(side=tk.RIGHT)

            btn_view = create_button(btn_frame, "🔍", 
                                lambda u=user: self.show_user_details(u['username']),
                                width=3)
            btn_view.pack(side=tk.LEFT, padx=2)

            btn_delete = create_button(btn_frame, "❌", 
                                    lambda u=user: self.delete_user(u['username']),
                                    style="Danger.TButton",
                                    width=3)
            btn_delete.pack(side=tk.LEFT, padx=2)
        
        # Adiciona UM botão "Voltar" no final
        btn_back = create_button(parent, "Voltar", self.switch_to_main)
        btn_back.pack(pady=20)
    
        self.switch_to_view()

    def show_user_details(self, username):
        """Mostra os detalhes de um usuário específico"""
        self.clear_frame(self.view_frame)
        
        # Encontra o usuário na lista
        user = next((u for u in self.data_manager.users_data if u['username'] == username), None)
        
        if not user:
            messagebox.showerror("Erro", "Usuário não encontrado!")
            return
        
        # Título com o nome do usuário
        create_label(self.view_frame, f"Detalhes de {username}", 
                    font=("Segoe UI Semibold", 16)).pack(pady=10)
        
        # Texto com os dados JSON
        text = create_text(self.view_frame, height=15)
        text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        text.insert(tk.END, json.dumps(user, indent=4))  # <--- Alterado para usar o user encontrado
        text.config(state=tk.DISABLED)
        
        # Botão Voltar
        btn_back = create_button(self.view_frame, "Voltar", self.view_users)
        btn_back.pack(pady=20)
        
        self.switch_to_view()

    def delete_user(self, username):
        try:
            # Encontra o usuário pelo username
            user = next((u for u in self.data_manager.users_data if u['username'] == username), None)
            if user and messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir {username}?"):
                # Exclui o arquivo físico
                self.data_manager.delete_user(user['filename'])
                # Recarrega os dados
                self.data_manager.load_users()
                self.view_users()  # Atualiza a interface
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao excluir: {str(e)}")

    def clear_frame(self, frame):
        """Limpa todos os widgets de um frame"""
        for widget in frame.winfo_children():
            widget.destroy()

    def safe_canvas_update(self, event=None):
        try:
            if self.frame_buffer and self.running:
                self.canvas_image = ImageTk.PhotoImage(self.frame_buffer)
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_image)
        except Exception as e:
            print(f"Canvas update error: {e}")

    def update_canvas(self):
        if self.running and self.canvas_image:
            try:
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_image)
            except tk.TclError:
                pass

    def authenticate(self):
        if not self.face_recognition.face_landmarks_data or (time.time() - self.face_recognition.last_face_detection) > 0.5:
            print("Nenhum rosto detectado!")
            self.face_recognition.face_landmarks_data = []
            return

        votes = 0
        detected_user = None
        
        for _ in range(5):
            if self.face_recognition.face_landmarks_data:
                normalized_current = self.face_recognition.normalized_current = self.face_recognition.normalize_landmarks(self.face_recognition.face_landmarks_data)
            for user in self.data_manager.users_data:
                saved_landmarks = user['landmarks']
                normalized_data = [self.face_recognition.normalize_landmarks(sample) for sample in saved_landmarks]
                if self.face_recognition.compare_faces(normalized_current, normalized_data):
                    votes += 1
                    detected_user = user['username']
                    break
        
        if votes >= 3 and detected_user:
            print(f"Login efetuado como {detected_user}")
            self.current_user = detected_user
            self.switch_to_authenticated()
        else:
            print("Autenticação falhou. Rosto não reconhecido.")
            self.current_user = None

    def start_face_mesh(self):
        self.face_recognition.stop()
        self.canvas.delete("all")
        self.running = True
        self.face_recognition.temp_landmarks = []
        self.currently_registering = False
        self.switch_to_mesh()
        threading.Thread(target=self.face_recognition.run_face_mesh, daemon=True).start()

    def stop_face_mesh(self):
        self.running = False
        self.face_recognition.stop()
        self.root.after(100, self.switch_to_main)

    def save_landmarks(self):
        if self.face_recognition.face_landmarks_data:
            if len(self.face_recognition.temp_landmarks) < 5:
                normalized = self.face_recognition.normalize_landmarks(self.face_recognition.face_landmarks_data)
                self.face_recognition.temp_landmarks.append(normalized)
                print(f"Captura {len(self.face_recognition.temp_landmarks)}/5 salva.")

        if len(self.face_recognition.temp_landmarks) == 5 and not self.currently_registering:
            self.currently_registering = True
            
            # Verificação de rosto existente
            if self._face_already_registered():
                messagebox.showerror("Erro", "Este rosto já está cadastrado no sistema!")
                self.face_recognition.temp_landmarks.clear()
                self.currently_registering = False
                return

            username = simpledialog.askstring("Cadastro", "Digite um nome para o usuário:")
            
            if username:
                try:
                    self.data_manager.add_user(username, self.face_recognition.temp_landmarks.copy())
                    print(f"Usuário {username} cadastrado com sucesso!")
                except ValueError as e:
                    messagebox.showerror("Erro", str(e))
            else:
                print("Cadastro cancelado.")
            
            self.face_recognition.temp_landmarks.clear()
            self.currently_registering = False

    def _face_already_registered(self):
        """Verifica se qualquer uma das 5 amostras já existe no sistema"""
        current_samples = self.face_recognition.temp_landmarks
        
        for user in self.data_manager.users_data:
            stored_samples = user['landmarks']  # Lista de amostras do usuário
            
            # Compara cada amostra atual com todas as armazenadas
            for current in current_samples:
                for stored in stored_samples:
                    if self.face_recognition.compare_faces(current, [stored]):
                        return True
        return False

    def enter_application(self):
        if self.data_manager.users_data:
            self.running = True
            self.switch_to_auth()
            threading.Thread(target=self.face_recognition.run_face_mesh, daemon=True).start()
        else:
            print("Nenhuma informação salva. Não é possível entrar.")

    def switch_to_mesh(self):
        self.main_frame.pack_forget()
        self.mesh_frame.pack()

    def switch_to_main(self):
        self.running = False
        self.face_recognition.stop()
        self.current_user = None
        for frame in [
            self.mesh_frame, 
            self.view_frame, 
            self.auth_frame, 
            self.authenticated_frame
        ]:
            frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.face_recognition.temp_landmarks = []
        self.currently_registering = False
        self.canvas.delete("all")

    def switch_to_view(self):
        self.main_frame.pack_forget()
        self.view_frame.pack()

    def switch_to_auth(self):
        self.main_frame.pack_forget()
        self.auth_frame.pack()

    def switch_to_authenticated(self):
        self.auth_frame.pack_forget()
        self.authenticated_frame.pack()
        self.lbl_success.config(text=f"Bem-vindo, {self.current_user}!")
    
