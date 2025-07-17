# login_system.py

class Login:
    def __init__(self):
        self.users = {
            "usuario1": "clave123",
            "admin": "adminpass",
            "testuser": "testpass"
        }

    def login(self, username, password):
        """
        Intenta autenticar a un usuario con el nombre de usuario y la contraseña proporcionados.

        Args:
            username (str): El nombre de usuario a autenticar.
            password (str): La contraseña a verificar.

        Returns:
            bool: True si la autenticación es exitosa, False en caso contrario.
        """
        if username in self.users:
            if self.users[username] == password:
                print(f"Login exitoso para el usuario: {username}")
                return True
            else:
                print(f"Error de login: Contraseña incorrecta para {username}")
                return False
        else:
            print(f"Error de login: Usuario '{username}' no encontrado")
            return False

    def change_password(self, username, old_password, new_password):
        """
        Permite a un usuario cambiar su contraseña.

        Args:
            username (str): El nombre de usuario.
            old_password (str): La contraseña actual del usuario.
            new_password (str): La nueva contraseña.

        Returns:
            bool: True si la contraseña se cambió con éxito, False en caso contrario.
        """
        if self.login(username, old_password):  # Reusa la lógica de login para verificar la contraseña antigua
            if old_password == new_password:
                print("Error: La nueva contraseña no puede ser igual a la anterior.")
                return False
            self.users[username] = new_password
            print(f"Contraseña cambiada exitosamente para {username}")
            return True
        else:
            print(f"Error al cambiar contraseña: Autenticación fallida para {username}")
            return False

# Ejemplo de uso (opcional, para probar manualmente)
if __name__ == "__main__":
    system = Login()

    print("\n--- Pruebas manuales ---")
    system.login("usuario1", "clave123")
    system.login("admin", "wrongpass")
    system.login("nonexistent", "anypass")

    print("\n--- Cambio de contraseña ---")
    system.change_password("usuario1", "clave123", "nueva_clave456")
    system.login("usuario1", "nueva_clave456")
    system.change_password("usuario1", "clave123", "otra_clave") # Debería fallar
    system.change_password("admin", "adminpass", "adminpass") # Debería fallar (misma contraseña)