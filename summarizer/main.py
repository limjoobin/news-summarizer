from vllm import LLM


llm = LLM(model="facebook/bart-large-cnn")


def main():
    print("Hello from summarizer!")


if __name__ == "__main__":
    main()
