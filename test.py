import openai
openai.api_base = "http://192.168.8.103:4891/v1"

openai.api_key = "tits"

def test_completion():
	model = "gpt4all-falcon-q4_0"
	prompt = "What is the great wall of china"
	response = openai.Completion.create(
		model = model,
		prompt = prompt,
		max_tokens=2000,
		tempurature=0.28,
		top_p=0.95,
		n=1,
		echo=True,
		stream=False
	)
	print("Tits")
	
test_completion()
