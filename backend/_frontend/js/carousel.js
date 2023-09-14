const prevBtn = document.querySelector('.carousel .carousel-button.prev');
const nextBtn = document.querySelector('.carousel .carousel-button.next');
const images = document.querySelectorAll('.carousel img.full');
let currIdx = 0; 

const thumbnails = document.querySelectorAll('.review-detail .thumbnails img.thumb_img');


function handlePrevClick(e){

    if(currIdx >0 ){
        images[currIdx].classList.add('hidden');
        thumbnails[currIdx].classList.add('inactive');
        currIdx--; 
        images[currIdx].classList.remove('hidden');
        thumbnails[currIdx].classList.remove('inactive');
        }   
}


function handleNextClick(e){

    if(currIdx < images.length -1 ){
    images[currIdx].classList.add('hidden');
    thumbnails[currIdx].classList.add('inactive');
    currIdx++; 
    images[currIdx].classList.remove('hidden');
    thumbnails[currIdx].classList.remove('inactive');
    }   
}

prevBtn.addEventListener('click',handlePrevClick)
nextBtn.addEventListener('click',handleNextClick)


//  썸네일 핸들러 

function handleThumbnailClick(e){
    
    images[currIdx].classList.add('hidden');
    thumbnails[currIdx].classList.add('inactive');
    currIdx = e.target.dataset.index;
    images[currIdx].classList.remove('hidden');
    thumbnails[currIdx].classList.remove('inactive');
}
for (let thumbnail of thumbnails){
    thumbnail.addEventListener('click',handleThumbnailClick);
}