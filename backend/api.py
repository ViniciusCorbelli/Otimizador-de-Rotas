from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from docplex.mp.model import Model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)

@app.post("/otimizar/")
async def otimizar(request : Request):
    data = await request.json()

    #Remove o ponto final
    n=int(data['total']-1)

    
    pontos=[i for i in range(n)]
    arcos = [(i,j) for i in pontos for j in pontos if i!=j]
    distancia = {}

    #Seta as posições no objeto
    for obj in data['distancias']:
        i = int(obj['saida'])
        j = int(obj['chegada'])
        if (i != j) & (i < n) & (j < n):
            distancia.update({(i, j): int(obj['distancia'])})


    mdl=Model('TSP')

    #Cria as variaveis binarias
    x=mdl.binary_var_dict(arcos,name='x')
    d=mdl.continuous_var_dict(pontos,name='d')

    mdl.minimize(mdl.sum(distancia[i]*x[i] for i in arcos))

    #De cada ponto so sai um arco
    #Retorna do ponto j para i somento se Xij = 1
    for c in pontos:
        mdl.add_constraint(mdl.sum(x[(i,j)] for i,j in arcos if i==c)==1, 
                        ctname='saida_%d'%c)

    #So chega um arco neste ponto
    #So vai do ponto j para o i se Xij = 1
    for c in pontos:
        mdl.add_constraint(mdl.sum(x[(i,j)] for i,j in arcos if j==c)==1, 
                        ctname='chegada_%d'%c)
    
    #Elimina as subrotas
    #Ui - Uj + N * Xij <= n -1 (i = 2,...,n, i != j)
    for i,j in arcos:
        if j!=0:
            mdl.add_indicator(x[(i,j)],d[i]+1==d[j], 
                            name='ordem_(%d,_%d)'%(i, j))

    mdl.parameters.timelimit=120
    mdl.parameters.mip.strategy.branch=1
    mdl.parameters.mip.tolerances.mipgap=0.15

    mdl.solve(log_output=False)

    #Cria o retorno
    response = []
    arcos_activos = [i for i in arcos if x[i].solution_value > 0.9]
    for i,j in arcos_activos:
        response.append([int(i), int(j)])

    return {
        "response" : str(response)
    }
    