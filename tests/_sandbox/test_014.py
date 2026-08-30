from libcore_hng.core.base_api_model import BaseApiModel

class ApiModel(BaseApiModel):
    
    prompt:str = ''
    
    
models = ApiModel()

models.prompt ="AAA"

print(models.prompt)
