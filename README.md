# OfflineDownloadTool
Download Center for Posit Products

This tool is used to generate a list of download links for Posit Products as well as R, Python and Quarto. This tool has been published here:

https://colorado.posit.co/rsc/OfflineDownloads/

Using this command: 

`rsconnect deploy api  --server https://colorado.posit.co/rsc --api-key ssHhvo9O28YEHfZJ7a8gRUcRtW3n7tbB ./ wbi.so`

### WBI

This Flask application relies on https://github.com/sol-eng/wbi specifically the c_lib branch. Once you're on that branch, just jupm into WSL and run this command to regenerate the wbi.so file that this Flask App relies on:

`go build -buildmode=c-shared -o wbi.so`

Then you can test and re-publish.
