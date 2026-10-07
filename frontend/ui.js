(() => {
  const fileInput=document.querySelector('#file'),drop=document.querySelector('#drop'),preview=document.querySelector('#preview'),videoPreview=document.querySelector('#video-preview'),analyze=document.querySelector('#analyze'),toast=document.querySelector('#toast');
  let currentUrl=null;
  function say(message){toast.textContent=message;toast.classList.add('on');setTimeout(()=>toast.classList.remove('on'),2600)}
  function clearResults(){document.querySelector('#result').classList.remove('show');document.querySelector('#empty-result').style.display='block';const dock=document.querySelector('#scene-report-dock');if(dock)dock.classList.remove('show');const host=document.querySelector('#scene-report-host');if(host)host.replaceChildren()}
  function setFile(file){
    if(!file)return;
    const video=/^video\//i.test(file.type)||/\.(mp4|webm|mov|m4v)$/i.test(file.name);
    const image=/^image\/(jpeg|png|webp|gif)$/i.test(file.type)||/\.(jpe?g|png|webp|gif)$/i.test(file.name);
    if(!video&&!image){say('Choose a JPG, PNG, WEBP, GIF, MP4, WEBM, or MOV file.');return}
    const limit=video?100:15;
    if(file.size>limit*1024*1024){say(`That ${video?'video':'image'} is over the ${limit} MB limit.`);return}
    if(currentUrl)URL.revokeObjectURL(currentUrl);
    currentUrl=URL.createObjectURL(file);window.roadwatchFile=file;window.roadwatchOriginalUrl=currentUrl;
    preview.removeAttribute('src');videoPreview.pause();videoPreview.removeAttribute('src');videoPreview.load();
    drop.classList.remove('has-image','has-video');
    if(video){videoPreview.src=currentUrl;drop.classList.add('has-video')}
    else{preview.src=currentUrl;preview.alt='Uploaded evidence: '+file.name;drop.classList.add('has-image')}
    document.querySelector('#filebadge').textContent=file.name+' · '+(file.size/1024/1024).toFixed(1)+' MB';
    document.querySelector('#uploadstatus').textContent=video?'Video ready · up to 30 frames will be sampled':'Image ready for review';
    document.querySelector('#remove').style.display='inline';analyze.disabled=false;clearResults();
  }
  document.querySelector('#choose').addEventListener('click',()=>fileInput.click());
  document.querySelector('#sample').addEventListener('click',()=>{try{const encoded=window.roadwatchSamplePhotoData;if(!encoded)throw new Error('Sample photo is unavailable; reload the page.');const bytes=Uint8Array.from(atob(encoded.split(',')[1]),c=>c.charCodeAt(0));setFile(new File([bytes],'sample-triple-riding.jpg',{type:'image/jpeg'}))}catch(error){say(error.message)}});
  document.querySelector('#helmet-sample').addEventListener('click',()=>{try{const encoded=window.roadwatchHelmetSampleData;if(!encoded)throw new Error('Helmet example is unavailable.');const bytes=Uint8Array.from(atob(encoded.split(',')[1]),c=>c.charCodeAt(0));setFile(new File([bytes],'sample-helmet-review.jpg',{type:'image/jpeg'}))}catch(error){say(error.message)}});
  document.querySelector('#sample-video').addEventListener('click',()=>{try{const encoded=window.roadwatchSampleVideoData;if(!encoded)throw new Error('Sample video is unavailable; reload the page.');const bytes=Uint8Array.from(atob(encoded.split(',')[1]),c=>c.charCodeAt(0));setFile(new File([bytes],'roadwatch-sample-video.webm',{type:'video/webm'}))}catch(error){say(error.message)}});
  drop.addEventListener('click',event=>{if(!drop.classList.contains('has-image')&&!drop.classList.contains('has-video')&&!event.target.closest('button'))fileInput.click()});
  fileInput.addEventListener('change',()=>{setFile(fileInput.files[0]);fileInput.value=''});
  for(const name of ['dragenter','dragover'])drop.addEventListener(name,event=>{event.preventDefault();drop.classList.add('drag')});
  for(const name of ['dragleave','drop'])drop.addEventListener(name,event=>{event.preventDefault();drop.classList.remove('drag')});
  drop.addEventListener('drop',event=>setFile(event.dataTransfer.files[0]));
  document.querySelector('#remove').addEventListener('click',()=>{if(currentUrl)URL.revokeObjectURL(currentUrl);currentUrl=null;window.roadwatchFile=null;window.roadwatchOriginalUrl=null;preview.removeAttribute('src');videoPreview.pause();videoPreview.removeAttribute('src');videoPreview.load();drop.classList.remove('has-image','has-video');document.querySelector('#filebadge').textContent='';document.querySelector('#uploadstatus').textContent='No image or video selected';document.querySelector('#remove').style.display='none';analyze.disabled=true;clearResults()});
})();
