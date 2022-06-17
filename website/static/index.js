function deleteImage(imageId) {
    fetch("/delete-image", {
        method: "POST",
        body: JSON.stringify({imageId: imageId}),
    }).then((_res) => {
        window.location.href = "/gallery";
    });
}

function deletePage(pageId) {
    fetch("/delete-page", {
        method: "POST",
        body: JSON.stringify({pageId: pageId}),
    }).then((_res) => {
        window.location.href = "/";
    });
}

function sortPage(sortPage){
    fetch("/sort-page",{
        method:"POST",
        body:JSON.stringify({sortStatus:sortPage}),
    }).then((_res)=>{
        window.location.href = "/";
    })
}

sessionStorage.setItem('sortStatus','UP');

