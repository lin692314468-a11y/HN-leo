// File drags use the same validation and replacement flow as the file picker.
function isFileDrag(event){return Array.from(event.dataTransfer?.types||[]).includes('Files')||!!event.dataTransfer?.files?.length;}
function bindFileDrop(zone,onFiles){
  let depth=0;
  const reset=()=>{depth=0;zone.classList.remove('drop-active')};
  zone.addEventListener('dragenter',event=>{if(!isFileDrag(event))return;event.preventDefault();event.stopPropagation();depth++;zone.classList.add('drop-active')});
  zone.addEventListener('dragover',event=>{if(!isFileDrag(event))return;event.preventDefault();event.stopPropagation();event.dataTransfer.dropEffect='copy'});
  zone.addEventListener('dragleave',event=>{event.stopPropagation();depth=Math.max(0,depth-1);if(!depth)reset()});
  zone.addEventListener('drop',event=>{if(!isFileDrag(event))return;event.preventDefault();event.stopPropagation();reset();onFiles(Array.from(event.dataTransfer.files||[]))});
}
