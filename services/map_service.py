import requests
from fastapi import HTTPException


def buscar_pontos(lat: float, lon: float):
    url = "https://overpass-api.de/api/interpreter"

    query = f"""
    [out:json][timeout:25];
    node
      ["amenity"="recycling"]
      (around:5000,{lat},{lon});
    out body;
    """

    try:
        response = requests.post(
            url,
            data=query.encode("utf-8"),
            headers={"Content-Type": "text/plain; charset=utf-8"},
            timeout=30,
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro ao conectar no Overpass: {str(e)}")

    print("STATUS OVERPASS:", response.status_code)
    print("RESPOSTA OVERPASS:", response.text[:500])

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Overpass retornou status {response.status_code}: {response.text[:300]}"
        )

    try:
        data = response.json()
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail=f"Overpass não retornou JSON válido. Resposta: {response.text[:300]}"
        )

    pontos_formatados = []

    for item in data.get("elements", []):
        tags = item.get("tags", {})

        tipos = []

        if tags.get("recycling:glass") == "yes":
            tipos.append("vidro")
        if tags.get("recycling:paper") == "yes":
            tipos.append("papel")
        if tags.get("recycling:plastic") == "yes":
            tipos.append("plástico")
        if tags.get("recycling:electronics") == "yes":
            tipos.append("eletrônicos")

        pontos_formatados.append({
            "nome": tags.get("name", "Ponto de Reciclagem"),
            "latitude": item.get("lat"),
            "longitude": item.get("lon"),
            "tipos": tipos if tipos else ["reciclagem geral"]
        })

    return pontos_formatados