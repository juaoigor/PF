const editor = new EditorJS({
  holderId: "editorJS",
  tools:{
    header: {
      class: Header,
      inlineToolbar: true
    },
    image: {
      class: ImageTool,
        config: {
        endpoints: { byFile: '/uploader', byUrl: '/uploader' }
      }
    },
    list: {
      class: List,
      inlineToolbar: true,
      config: { defaultStyle: 'unordered' }
    },
    table: {
      class: Table,
      inlineToolbar: true,
      config: { rows: 2, cols: 3, ,
    },
    quote: {
      class: Quote,
      inlineToolbar: true,
      config: { quotePlaceholder: 'Enter a quote', captionPlaceholder: 'Quote\'s author', }
    },
    delimiter: { class: Delimiter },
    code: { class: CodeTool },
    Marker: { class: Marker }
  }
});

function doSave() {
	editor.save().then((outputData) => {
    document.getElementById("idTexto").value = JSON.stringify(outputData)
  })
}
