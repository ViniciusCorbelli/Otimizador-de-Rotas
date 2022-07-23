package br.com.ontoforall.owlapi.resources;

import javax.ws.rs.Consumes;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.Response.Status;

import org.json.JSONObject;

import br.com.ontoforall.owlapi.model.Info;

@Path("resouce")
public class Rotas {

	public Rotas() {

	}

	@POST
	@Path("otimizar")
	@Produces(MediaType.TEXT_PLAIN)
	@Consumes(MediaType.APPLICATION_JSON)
	public Response validacao(String ontologia) {
		
	    int n = 6;
	    double[][] distanceMatrix = new double[n][n];
	    for (double[] row : distanceMatrix) java.util.Arrays.fill(row, 10000);
	    distanceMatrix[1][4] = distanceMatrix[4][1] = 2;
	    distanceMatrix[4][2] = distanceMatrix[2][4] = 4;
	    distanceMatrix[2][3] = distanceMatrix[3][2] = 6;
	    distanceMatrix[3][0] = distanceMatrix[0][3] = 8;
	    distanceMatrix[0][5] = distanceMatrix[5][0] = 10;
	    distanceMatrix[5][1] = distanceMatrix[1][5] = 12;

	    Info solver = new Info(distanceMatrix);

	    JSONObject resp = new JSONObject();
	    resp.put("rota", solver.getTour());
	    resp.put("distancia", solver.getTourCost());
		
		return Response.status(Status.ACCEPTED).entity(resp.toString()).build();
	}

}
