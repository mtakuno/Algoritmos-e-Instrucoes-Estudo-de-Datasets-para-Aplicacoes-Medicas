#################################################################################
# @ file:  4_run_model_extract_sum
# @ brief: Sumarização por QA
#################################################################################
# Extrai as principais informações como um question and answer (reestruturando o
# o prompt baseline), e depois resumindo com as principais informações.
#
# @ author: Melissa
# @ date: 26-Maio-2026
# @ verion: 1.0
#################################################################################

# imports
import ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter

# splitter init
splitter = RecursiveCharacterTextSplitter(
    chunk_size=3000,
    chunk_overlap=500,
    separators=["\n\n", "\n", ".", " ", ""]
)

# configurando o ambiente
model = "llama3.1:8b"
method = "extract_sum"
temperature = 0.1
file_number = "4"

directory_baseline_prompt = "./in/prompts/baseline_prompt.md"
directory_extract_sum_prompt = "./in/prompts/extract_sum_prompt.md"
directory_map_reduce_prompt = "./in/prompts/map_reduce_prompt.md"
directory_dialog_in = "./in/relatos/relato_unico.md"
directory_dialog_out = f"./out/{file_number}_{method}_{model}.md"


# variaveis globais
answers = []

# processamento dialogo e prompts
with (open(directory_dialog_in, encoding="utf-8") as f_in,
      open(directory_map_reduce_prompt, encoding="utf-8") as f_map_prompt,
      open(directory_extract_sum_prompt, encoding="utf-8") as f_extract_sum_prompt):
    texto = f_in.read()
    extract_sum_prompt = f_extract_sum_prompt.read()
    map_reduce_prompt = f_map_prompt.read()

chunks = splitter.split_text(texto)
print(f"Iniciando processamento. Total de chunks: {len(chunks)}")


# chama modelo local via Ollama e itera sobre os demais chunks atualizando o resumo
for i in range(0, len(chunks)):
    print(f"Atualizando resumo com o chunk {i+1}/{len(chunks)}...")
    prompt = extract_sum_prompt.format(texto=chunks[i])

    #  Chama o modelo para iterar e gerar uma nova resposta
    response = ollama.generate(model=model, prompt=prompt, options={'temperature':temperature})
    answers.append(response['response'])

# unifica todas informações
union_extracted_info = "\n\n--- answers ---\n\n".join(answers)
prompt = map_reduce_prompt.format(union_summaries=union_extracted_info)


# chama modelo local via ollama e processa todo texto
response = ollama.generate(model=model, prompt=prompt, options={'temperature':temperature})
final_sum = response['response']

# mostra a saída
print("Resposta do modelo:\n")
print(final_sum)

# salvar saída em arquivo md
with open(directory_dialog_out, 'w', encoding="utf-8") as f:
    note_structed = f"""
    '''
    ### PRINCIPAIS INFORMAÇÕES
    Arquivo: {file_number}
    Modelo: {model}
    Tipo: Sumarização por QA (extrai as principais informações, junta-as e cria um resumo na estrutura)
    Chunk size: {splitter._chunk_size}
    Overlap: {splitter._chunk_overlap}
    '''

    {final_sum}
    """

    f.write(note_structed)
