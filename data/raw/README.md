# data/raw/ — fuente original (no versionada)

Aquí va el archivo fuente:

```
1.Base de Datos Clientes 2017.xlsx   (hoja «Hoja1», ~4.178 filas, 2016–2024)
```

**No está en el repositorio a propósito**: contiene nombres, ciudades y montos
de compra de ~4.300 clientes reales (Ley 1581 de 2012). La carpeta entera está
en `.gitignore`.

Sin este archivo, las etapas 1-4 del pipeline (`run.sh`) se omiten. La etapa 5
(análisis y gráficos) funciona igual, porque corre sobre el CSV ya anonimizado
que sí está en el repo: [`../processed/ventas.csv`](../processed/ventas.csv).
