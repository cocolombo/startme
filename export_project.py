
import os

# Liste des dossiers à ignorer
IGNORE_DIRS = {'.venv', '__pycache__', '.git', '.idea', 'migrations'}
# Extensions à inclure
INCLUDE_EXTS = {'.py', '.html', '.js', '.css'}

def export_code():
    """Concatène tous les fichiers .py/.html/.js/.css du projet dans projet_context.txt pour analyse par un LLM."""
    output_file = 'projet_context.txt'

    with open(output_file, 'w', encoding='utf-8') as outfile:
        # On parcourt tout le dossier
        for root, dirs, files in os.walk('.'):
            # On retire les dossiers ignorés
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in INCLUDE_EXTS and file != 'export_project.py':
                    file_path = os.path.join(root, file)

                    # Écriture de l'entête du fichier
                    outfile.write(f"\n{'= ' *50}\n")
                    outfile.write(f"FICHIER: {file_path}\n")
                    outfile.write(f"{'= ' *50}\n\n")

                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"Erreur de lecture: {e}")

                    outfile.write("\n")

    print(f"✅ Terminé ! Tout le code est dans '{output_file}'.")
    print("Vous pouvez maintenant uploader ce fichier dans Gemini.")

if __name__ == "__main__":
    export_code()

