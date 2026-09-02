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
from langchain_text_splitters import RecursiveCharacterTextSplitter
from medic_evaluation import MEDIC_main

# splitter init
splitter = RecursiveCharacterTextSplitter(
    chunk_size=3000,
    chunk_overlap=500,
    separators=["\n\n", "\n", ".", " ", ""]
)


# configuracao de modelos e caminhos
# automatizar processo de chamada de mais de um modelo
methods = ["stuff"]
models = ["medgemma:4b"]
temperature = 0.1

directory_baseline_prompt = "./in/prompts/baseline_prompt.md"
directory_extract_sum_prompt = "./in/prompts/extract_sum_prompt.md"
directory_map_reduce_prompt = "./in/prompts/map_reduce_prompt.md"
directory_refine_prompt = "./in/prompts/refine_prompt.md"

directory_dialog_in = "./in/relatos/relato_unico.md"


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
        safe_model_name = model.replace(":", "_")

        print(f"Iniciando processamento (stuff), modelo atual {model}")
        response = ollama.generate(model=model, prompt=prompt, options={'temperature': temperature})
        note_sum = response['response']

        directory_dialog_out = f"./out/{file_number}_{method}_{safe_model_name}.txt"
        with open(directory_dialog_out, 'w', encoding="utf-8") as f:
            note_structed = f"""
            '''
            ### PRINCIPAIS INFORMAÇÕES
            Arquivo: {file_number}
            Modelo: {model}
            Tipo: Sumarização direta (Stuff)
            '''

            {note_sum}"""
            f.write(note_structed)


def run_model_map_reduce():
    partial_summaries = []
    for model in models:
        print(f"Iniciando processamento (map reduce), modelo atual {model}")

        for i in range(0, len(chunks)):
            print(f"Atualizando resumo com o chunk {i+1}/{len(chunks)}...")
            prompt = baseline_prompt.format(texto=chunks[i])

            response = ollama.generate(model=model, prompt=prompt, options={'temperature': temperature})
            partial_summaries.append(response['response'])

        union_summaries = "\n\n--- partial summaries ---\n\n".join(partial_summaries)
        prompt = map_reduce_prompt.format(union_summaries=union_summaries)

        response = ollama.generate(model=model, prompt=prompt, options={'temperature': temperature})
        final_sum = response['response']

        directory_dialog_out = f"./out/{file_number}_{method}_{model}.md"
        with open(directory_dialog_out, 'w', encoding="utf-8") as f:
            note_structed = f"""
            '''
            ### PRINCIPAIS INFORMAÇÕES
            Arquivo: {file_number}
            Modelo: {model}
            Tipo: {method}
            Chunk size: {splitter._chunk_size}
            Overlap: {splitter._chunk_overlap}
            '''

            {final_sum}
            """
            f.write(note_structed)


def run_model_refine():
    for model in models:
        print(f"Iniciando processamento, modelo atual {model}")
        prompt = baseline_prompt.format(texto=chunks[0])
        response = ollama.generate(model=model, prompt=prompt)
        note_sum = response['response']

        # chama modelo local via Ollama e itera sobre os demais chunks atualizando o resumo
        for i in range(1, len(chunks)):
            print(f"Atualizando resumo com o chunk {i+1}/{len(chunks)}...")
            prompt = refine_prompt.format(texto=chunks[i])

            response = ollama.generate(model=model, prompt=prompt, options={'temperature': temperature,  "num_predict": 2000})
            note_sum = response['response']
            print(f"Tamanho do resumo atual: {len(note_sum)}...")

        directory_dialog_out = f"./out/{file_number}_{method}_{model}.md"
        with open(directory_dialog_out, 'w', encoding="utf-8") as f:
            note_structed = note_structed = f"""
            '''
            ### PRINCIPAIS INFORMAÇÕES

            Arquivo: {file_number}
            Modelo: {model}
            Tipo: {method}
            Chunk size: {splitter._chunk_size}
            Overlap: {splitter._chunk_overlap}
            '''

            {note_sum}
            """
            f.write(note_structed)



def run_model_extract_sum():
    answers = []

    for model in models:
        print(f"Iniciando processamento, modelo atual {model}")

        for i in range(0, len(chunks)):
            print(f"Atualizando resumo com o chunk {i+1}/{len(chunks)}...")
            prompt = extract_sum_prompt.format(texto=chunks[i])
            response = ollama.generate(model=model, prompt=prompt, options={'temperature': temperature})
            answers.append(response['response'])

        union_extracted_info = "\n\n--- answers ---\n\n".join(answers)
        prompt = map_reduce_prompt.format(union_summaries=union_extracted_info)

        response = ollama.generate(model=model, prompt=prompt)
        final_sum = response['response']

        directory_dialog_out = f"./out/{file_number}_{method}_{model}.md"
        with open(directory_dialog_out, 'w', encoding="utf-8") as f:
            note_structed = f"""
            '''
            ### PRINCIPAIS INFORMAÇÕES
            Arquivo: {file_number}
            Modelo: {model}
            Tipo: {method}
            Chunk size: {splitter._chunk_size}
            Overlap: {splitter._chunk_overlap}
            '''

            {final_sum}
            """
            f.write(note_structed)


# implementando protocolo de avaliação
directory_dialog_out = f"./out/1_stuff_llama3.1_8b.md"
evaluations_results = MEDIC_main.run_evaluation(directory_dialog_in, directory_dialog_out)
print(evaluations_results)


# # MAIN - chamada interativa dos métodos
# for method in methods:
#     if (method == "stuff"):
#         file_number = "1"
#         run_model_stuff()

#    if (method == "map_reduce"):
#        file_number = "2"
#        run_model_map_reduce()

#    if (method == "refine"):
#        file_number = "3"
#        run_model_refine()

#    if (method == "extract_sum"):
#        file_number = "4"
#        run_model_extract_sum()

#    else:
#        continue


