#################################################################################
# @ file: 1_run_model_stuff
# @ brief: Sumarização Direta (Stuff)
#################################################################################
# Consiste em inserir o prompt com o texto na integra para o modelo processar.
#
# @ author: Melissa
# @ date: 29-Maio-2026
# @ verion: 1.0
#################################################################################

# imports
import ollama

# configuracao de modelos e caminhos
model = "gemma2:9b-instruct-q4_0"
method = "stuff"
temperature = 0.1
file_number = "1"

safe_model = model.replace(":", "_").replace("/", "_")#for compatibility with linux and windows files
directory_baseline_prompt = "./in/prompts/baseline_prompt.md"
directory_dialog_in = "./in/relatos/relato_curto.md"
directory_dialog_out = f"./out/{file_number}_{method}_{safe_model}.md"


# processamento dialogo e prompts
with (open(directory_dialog_in, encoding="utf-8") as f_in,
      open(directory_baseline_prompt, encoding="utf-8") as f_prompt):
    texto = f_in.read()
    baseline_prompt = f_prompt.read()

prompt = baseline_prompt.format(texto=texto)

# chama modelo local via ollama e processa todo texto
response = ollama.generate(model=model, prompt=prompt, options={'temperature': temperature})
#response = ollama.generate(model=model, prompt=prompt)
note_sum = response['response']

# mostra a saída
print("Resposta do modelo:\n")
print(note_sum)

# criar e salvar saida em arquivo md
with open(directory_dialog_out, 'w', encoding="utf-8") as f:
    note_structed = f"""
    '''
    ### PRINCIPAIS INFORMAÇÕES
    Arquivo: {file_number}
    Modelo: {model}
    Tipo: Sumarização direta (Stuff)
    '''

    {note_sum}
    """

    f.write(note_structed)
