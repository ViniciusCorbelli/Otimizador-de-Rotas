from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import numpy as np
from docplex.mp.model import Model
import docplex.mp.solution as Solucion

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)

@app.post("/otimizar/")
async def otimizar(request : Request):
    data = await request.json()

    n=int(data['total'])
    pontos=[i for i in range(n)]
    arcos = [(i,j) for i in pontos for j in pontos if i!=j]
    distancia = {}

    for obj in data['distancias']:
        i = int(obj['saida'])
        j = int(obj['chegada'])
        d = int(obj['distancia'])
        if i != j:
            distancia.update({(i, j): d})

    mdl=Model('TSP')

    x=mdl.binary_var_dict(arcos,name='x')
    d=mdl.continuous_var_dict(pontos,name='d')

    mdl.minimize(mdl.sum(distancia[i]*x[i] for i in arcos))

    for c in pontos:
        mdl.add_constraint(mdl.sum(x[(i,j)] for i,j in arcos if i==c)==1, 
                        ctname='out_%d'%c)
    for c in pontos:
        mdl.add_constraint(mdl.sum(x[(i,j)] for i,j in arcos if j==c)==1, 
                        ctname='in_%d'%c)
    for i,j in arcos:
        if j!=0:
            mdl.add_indicator(x[(i,j)],d[i]+1==d[j], 
                            name='order_(%d,_%d)'%(i, j))

    mdl.parameters.timelimit=120
    mdl.parameters.mip.strategy.branch=1
    mdl.parameters.mip.tolerances.mipgap=0.15

    mdl.solve(log_output=False)

    response = []
    arcos_activos = [i for i in arcos if x[i].solution_value > 0.9]
    for i,j in arcos_activos:
        response.append([int(i), int(j)])

    return {
        "response" : str(response)
    }
    