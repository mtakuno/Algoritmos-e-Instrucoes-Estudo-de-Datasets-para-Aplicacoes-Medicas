#################################################################################
# @ file:  3_run_model_refine
# @ brief: Sumarização por refine
#################################################################################
# Sumariza o primeiro bloco e vai refinando com as outras informações.
#
# @ author: Melissa
# @ date: 26-Maio-2026
# @ verion: 1.0
#################################################################################

# imports
import ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter
import time

# inicialização da contagem de tempo
tempo_inicio = time.perf_counter()

# splitter init
splitter = RecursiveCharacterTextSplitter(
    chunk_size=3000,
    chunk_overlap=500,
    separators=["\n\n", "\n", ".", " ", ""]
)

# configurando o ambiente
model = "medgemma:4b"
method = "refine"
temperature = 0.1
file_number = "3"

directory_baseline_prompt = "./in/prompts/baseline_prompt.md"
directory_refine_prompt = "./in/prompts/refine_prompt.md"
directory_dialog_in = "./in/relatos/relato_unico.md"
directory_dialog_out = f"./out/{file_number}_{method}_{model}.md"

# processamento dialogo e prompts
with (open(directory_dialog_in, encoding="utf-8") as f_in,
      open(directory_baseline_prompt, encoding="utf-8") as f_prompt,
      open(directory_refine_prompt, encoding="utf-8") as f_refine_prompt):
    texto = f_in.read()
    baseline_prompt = f_prompt.read()
    refine_prompt = f_refine_prompt.read()

chunks = splitter.split_text(texto)

# chama modelo local via Ollama e processa a 1 chunk prompt da primeira chunk a ser processada
print(f"Iniciando processamento. Total de chunks: {len(chunks)}")

# chama modelo local via Ollama e processa a 1 chunk
prompt = baseline_prompt.format(texto=chunks[0])
response = ollama.generate(model=model, prompt=prompt, options={
                           'temperature': temperature})
note_sum = response['response']

# chama modelo local via Ollama e itera sobre os demais chunks atualizando o resumo
for i in range(1, len(chunks)):
    print(f"Atualizando resumo com o chunk {i+1}/{len(chunks)}...")
    prompt = refine_prompt.format(note_sum=note_sum, chunks=chunks[i])

    response = ollama.generate(model=model, prompt=prompt, options={
                               'temperature': temperature, "num_predict": 1750})
    note_sum = response['response']
    print(f"Tamanho do resumo atual: {len(note_sum)}...")


# mostra a saída
print("Resposta do modelo:\n")
print(note_sum)

# finaliza contagem de tempo
tempo_fim = time.perf_counter()
tempo = tempo_fim - tempo_inicio

# salvar saída em arquivo md
with open(directory_dialog_out, 'w', encoding="utf-8") as f:
    note_structed = note_structed = f"""
    '''
    ### PRINCIPAIS INFORMAÇÕES

    Arquivo: {file_number}
    Modelo: {model}
    Tipo: Sumarização por refine (Sumariza o primeiro bloco e vai refinando com as outras informações)
    Chunk size: {splitter._chunk_size}
    Overlap: {splitter._chunk_overlap}
    Tempo processamento: {tempo} segundos
    '''

    {note_sum}
    """
    f.write(note_structed)
