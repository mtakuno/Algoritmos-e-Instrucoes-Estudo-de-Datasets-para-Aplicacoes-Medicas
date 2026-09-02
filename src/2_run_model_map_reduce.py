#################################################################################
# @ file: 2_run_model_map_reduce
# @ brief: Sumarização por Map/Reduce
#################################################################################
# Sumariza todos os blocos e depois, resume os resumos.
#
# @ author: Melissa
# @ date: 08-Junho-2026
# @ verion: 1.0
#################################################################################

# imports
import ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter

# splitter init
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1024,
    chunk_overlap=154,
    separators=["\n\n", "\n", ".", " ", ""]
)

# configurando o ambiente
model = "medgemma:4b"
method = "map_reduce"
temperature = 0.1
file_number = "2"

directory_baseline_prompt = "./in/prompts/baseline_prompt.md"
directory_map_reduce_prompt = "./in/prompts/map_reduce_prompt.md"
directory_dialog_in = "./in/relatos/relato_unico.md"
directory_dialog_out = f"./out/{file_number}_{method}_{model}.md"

# variaveis globais
partial_summaries = []

# processamento dialogo e prompts
with (open(directory_dialog_in, encoding="utf-8") as f_in,
      open(directory_baseline_prompt, encoding="utf-8") as f_prompt,
      open(directory_map_reduce_prompt, encoding="utf-8") as f_map_prompt):
    texto = f_in.read()
    baseline_prompt = f_prompt.read()
    map_reduce_prompt = f_map_prompt.read()

chunks = splitter.split_text(texto)


# chama modelo local via Ollama e itera sobre os chunks resumindo separado
print(f"Iniciando processamento. Total de chunks: {len(chunks)}")

for i in range(0, len(chunks)):
    print(f"Atualizando resumo com o chunk {i+1}/{len(chunks)}...")
    prompt = baseline_prompt.format(texto=chunks[i])

    response = ollama.generate(model=model, prompt=prompt, options={'temperature':temperature})
    partial_summaries.append(response['response'])


# unifica todos os resumos parciais
union_summaries = "\n\n--- partial summaries ---\n\n".join(partial_summaries)
prompt = map_reduce_prompt.format(union_summaries=union_summaries)

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
    Tipo: Sumarização por Map/Reduce (Sumariza todos os blocos e depois, resume os resumos)
    Chunk size: {splitter._chunk_size}
    Overlap: {splitter._chunk_overlap}
    '''

    {final_sum}
    """

    f.write(note_structed)
