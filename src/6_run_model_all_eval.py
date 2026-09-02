#################################################################################
# @ file: 5_run_model_all
# @ brief: pipeline automatizada
#################################################################################
# Automatizar todos os processos "stuff", "map_reduce", "refine", "extract_sum",
# para rodar todos os modelos.
#
# @ author: Melissa
# @ date: 08-Jun-2026
# @ verion: 1.0
#################################################################################

# imports
import ollama
import time
from langchain_text_splitters import RecursiveCharacterTextSplitter

# configuracao de modelos e caminhos
# automatizar processo de chamada de mais de um modelo
directory_baseline_prompt = "./in/prompts/baseline_prompt.md"
directory_extract_sum_prompt = "./in/prompts/extract_sum_prompt.md"
directory_map_reduce_prompt = "./in/prompts/map_reduce_prompt.md"
directory_refine_prompt = "./in/prompts/refine_prompt.md"

directory_dialog_in = "./in/relatos/relato_unico.md"

#methods = ["stuff", "map_reduce", "refine", "extract_sum"]
methods = ["map_reduce", "refine", "extract_sum"]

models = ['mistral:7b', 'llama3.1:8b', 'ajindal/llama3.1-storm:8b',
          'thewindmom/llama3-med42-8b', 'cniongolo/biomistral', 'qwen3:8b',
          'medgemma:4b', 'gemma2:9b-instruct-q4_0', 'qwen2.5:7b', 'mistral:7b-instruct-v0.3-fp16']
          
temperature = 0.1
chunk_size = 4096
client = ollama.Client(timeout=180.0) #definindo um timeout de 3 minutos para o processamento de cada chunk (para cada chamada da llm)

# splitter init
splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=round(0.1*chunk_size),
    separators=["\n\n", "\n", ".", " ", ""]
)


# processamento dialogo e prompts
with (open(directory_dialog_in, encoding="utf-8") as f_in,
      open(directory_baseline_prompt, encoding="utf-8") as f_prompt,
      open(directory_refine_prompt, encoding="utf-8") as f_refine_prompt,
      open(directory_map_reduce_prompt, encoding="utf-8") as f_map_prompt,
      open(directory_extract_sum_prompt, encoding="utf-8") as f_extract_sum_prompt):
    texto = f_in.read()
    baseline_prompt = f_prompt.read()
    refine_prompt = f_refine_prompt.read()
    extract_sum_prompt = f_extract_sum_prompt.read()
    map_reduce_prompt = f_map_prompt.read()
chunks = splitter.split_text(texto)


# definindo funções especificas para cada método
def run_model_stuff():
    prompt = baseline_prompt.format(texto=texto)

    for model in models:
        begin = time.perf_counter()
        print(f"Iniciando processamento (stuff), modelo atual {model}")

        try:
            response = ollama.generate(model=model, prompt=prompt, options={'temperature': temperature})
            note_sum = response['response']

        except Exception as e:
            note_sum = "Ultrapassou o tempo limite de {timeout} segundos por chunk/chamada da llm}"


        end = time.perf_counter()
        total_time = end-begin

        safe_model = model.replace(":", "_").replace("/", "_") #for compatibility with linux and windows files
        directory_dialog_out = f"./out/{file_number}_{method}_{safe_model}.md"

        with open(directory_dialog_out, 'w', encoding="utf-8") as f:
            note_structed = f"""
            '''
            ### PRINCIPAIS INFORMAÇÕES
            Arquivo: {file_number}
            Modelo: {model}
            Tipo: Sumarização direta (Stuff)
            Tempo: {total_time}
            '''

            {note_sum}"""
            f.write(note_structed)


def run_model_map_reduce():
    partial_summaries = []
    for model in models:
        begin = time.perf_counter()

        print(f"Iniciando processamento (map reduce), modelo atual {model}")

        for i in range(0, len(chunks)):
            print(f"Atualizando resumo com o chunk {i+1}/{len(chunks)}...")
            prompt = baseline_prompt.format(texto=chunks[i])

            try:
                response = ollama.generate(model=model, prompt=prompt, options={'temperature': temperature})
                partial_summaries.append(response['response'])

            except Exception as e:
                final_sum = "Ultrapassou o tempo limite de {timeout} segundos por chunk/chamada da llm}"

        union_summaries = "\n\n--- partial summaries ---\n\n".join(partial_summaries)
        prompt = map_reduce_prompt.format(union_summaries=union_summaries)

        try:
            response = ollama.generate(model=model, prompt=prompt, options={'temperature': temperature})
            final_sum = response['response']

        except Exception as e:
            final_sum = "Ultrapassou o tempo limite de {timeout} segundos por chunk/chamada da llm}"

        end = time.perf_counter()
        total_time = end-begin

        safe_model = model.replace(":", "_").replace("/", "_") #for compatibility with linux and windows files
        directory_dialog_out = f"./out/{file_number}_{method}_{safe_model}.md"
        
        with open(directory_dialog_out, 'w', encoding="utf-8") as f:
            note_structed = f"""
            '''
            ### PRINCIPAIS INFORMAÇÕES
            Arquivo: {file_number}
            Modelo: {model}
            Tipo: {method}
            Chunk size: {splitter._chunk_size}
            Overlap: {splitter._chunk_overlap}
            Tempo: {total_time}            
            '''

            {final_sum}
            """
            f.write(note_structed)


def run_model_refine():
    for model in models:
        begin = time.perf_counter()

        print(f"Iniciando processamento, modelo atual {model}")
        prompt = baseline_prompt.format(texto=chunks[0])
        response = ollama.generate(model=model, prompt=prompt, options={'temperature': temperature})
        note_sum = response['response']

        # chama modelo local via Ollama e itera sobre os demais chunks atualizando o resumo
        for i in range(1, len(chunks)):
            print(f"Atualizando resumo com o chunk {i+1}/{len(chunks)}...")
            prompt = refine_prompt.format(note_sum=note_sum, chunks=chunks[i])
            
            try:
                response = ollama.generate(model=model, prompt=prompt, options={'temperature': temperature,  "num_predict": 2000})
                note_sum = response['response']
            
            except Exception as e:
                note_sum = "Ultrapassou o tempo limite de {timeout} segundos por chunk/chamada da llm}"

        end = time.perf_counter()
        total_time = end-begin

        safe_model = model.replace(":", "_").replace("/", "_") #for compatibility with linux and windows files
        directory_dialog_out = f"./out/{file_number}_{method}_{safe_model}.md"

        with open(directory_dialog_out, 'w', encoding="utf-8") as f:
            note_structed = note_structed = f"""
            '''
            ### PRINCIPAIS INFORMAÇÕES

            Arquivo: {file_number}
            Modelo: {model}
            Tipo: {method}
            Chunk size: {splitter._chunk_size}
            Overlap: {splitter._chunk_overlap}
            Tempo: {total_time}
            '''

            {note_sum}
            """
            f.write(note_structed)


def run_model_extract_sum():
    answers = []

    for model in models:
        begin = time.perf_counter()
        print(f"Iniciando processamento, modelo atual {model}")

        for i in range(0, len(chunks)):
            print(f"Atualizando resumo com o chunk {i+1}/{len(chunks)}...")
            prompt = extract_sum_prompt.format(texto=chunks[i])

            try:
                response = ollama.generate(model=model, prompt=prompt, options={'temperature': temperature})
                answers.append(response['response'])

            except Exception as e:
                final_sum = "Ultrapassou o tempo limite de {timeout} segundos por chunk/chamada da llm}"

        union_extracted_info = "\n\n--- answers ---\n\n".join(answers)
        prompt = map_reduce_prompt.format(union_summaries=union_extracted_info)

        try:
            response = ollama.generate(model=model, prompt=prompt, options={'temperature': temperature})
            final_sum = response['response']

        except Exception as e:
            final_sum = "Ultrapassou o tempo limite de {timeout} segundos por chunk/chamada da llm}"

        end = time.perf_counter()
        total_time = end-begin

        safe_model = model.replace(":", "_").replace("/", "_") #for compatibility with linux and windows files
        directory_dialog_out = f"./out/{file_number}_{method}_{safe_model}.md"

        with open(directory_dialog_out, 'w', encoding="utf-8") as f:
            note_structed = f"""
            '''
            ### PRINCIPAIS INFORMAÇÕES
            Arquivo: {file_number}
            Modelo: {model}
            Tipo: {method}
            Chunk size: {splitter._chunk_size}
            Overlap: {splitter._chunk_overlap}
            Tempo: {total_time}
            '''

            {final_sum}
            """
            f.write(note_structed)


# MAIN - chamada interativa dos métodos
for method in methods:
    if (method == "stuff"):
        file_number = "1"
        run_model_stuff()

    if (method == "map_reduce"):
        file_number = "2"
        run_model_map_reduce()

    if (method == "refine"):
        file_number = "3"
        run_model_refine()

    if (method == "extract_sum"):
        file_number = "4"
        run_model_extract_sum()
    

