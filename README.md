# TP0: Docker + Comunicaciones + Concurrencia

Alumno: Ugarte, Ricardo Martín

Padrón: 107870

## Parte 1: Introducción a Docker

### Ejercicio N°1

Mostrar como ejecutar `docker network`

### Ejercicio N°1.1

Mostrar como ejecutar

### Ejercicio N°2

Mostrar como ejecutar

### Ejercicio N°3

Mostrar como ejecutar

### Ejercicio N°4

Mostrar como ejecutar

## Parte 2: Repaso de Comunicaciones

### Protocolo de comunicación implementado

El flujo de la lotería es el siguiente:
1. El `cliente` (la agencia) va leyendo linea por linea desde su correspondiente archivo de apuestas. De esta forma las va acumulando en un mensaje hasta llegar a la cantidad máxima de apuestas por batch establecida en una constante, para luego enviarlo al `servidor`. Adicionalmente, se agrega en un header la cantidad de bytes a leer y un flag si se trata del último batch o no.

Si por ejemplo `BETS_PER_BATCH = 2` y la agencia $1$ lee las siguientes lineas, suponiendo que aún no llegó al final del archivo:

> Martin,Ugarte,44096365,11-04-2002,1000\
> Daniel,Degarbo,44125682,17-04-2003,7232

Enviará el siguiente mensaje:

> 78-0#Martin,Ugarte,44096365,11-04-2002,1000\tDaniel,Degarbo,44125682,17-04-2003,7232

Como se puede observar, el header y el payload están separados por un `#`, donde se indica que el payload es de 78 bytes y el flag 0 refiere a que aún quedan batchs por recibir. Al mismo tiempo, las apuestas se separan por el caracter especial `\t`

2. El `servidor` (la central) recibirá los batchs y por cada uno se ocupará de decodificarlos, transformándolos a objetos `Bet` y generando una lista para luego usar la función provista por la cátedra `store_bets()` y almacenar las apuestas en el archivo `bets.csv`. Cabe destacar que por cada batch recibido, el servidor manda un `ACK` al cliente para confirmar la recepción y esperar el siguiente batch. La razón es porque el tamaño de los paquetes es variable entonces el servidor no sabrá de antemano cuantos bytes fijos recibir.

3. Al recibir completamente todas las apuestas, el


### Ejercicio N°5

Mostrar como ejecutar

### Ejercicio N°6

Mostrar como ejecutar

### Ejercicio N°7

Mostrar como ejecutar

## Parte 3: Repaso de Concurrencia

### Mecanismos de sincronización utilizados

Mostrar mecanismos

### Ejercicio N°8

Mostrar como ejecutar
