// lazy load image 
document.addEventListener("DOMContentLoaded", function () {
    let images = document.querySelectorAll("img");

    if ("IntersectionObserver" in window) {
        let observer = new IntersectionObserver(function (entries, observer) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    let image = entry.target;
                    if (image.getAttribute("src") && image.getAttribute("data-src")) {
                        image.src = image.getAttribute("data-src");
                        image.removeAttribute("data-src");
                    }
                    observer.unobserve(image);
                }
            });
        });

        images.forEach(function (image) {
            if (image.getAttribute("src") && image.getAttribute("data-src")) {
                observer.observe(image);
            }
        });
    } else {
        // Fallback for browsers without Intersection Observer support
        images.forEach(function (image) {
            if (image.getAttribute("src") && image.getAttribute("data-src")) {
                image.src = image.getAttribute("data-src");
                image.removeAttribute("data-src");
            }
        });
    }
});

// show search bar 
const serachicon = document.querySelector('#search_button_nav');
const search_container = document.querySelector('#searchContainer');
serachicon.addEventListener('click', function () {
    search_container.classList.toggle('show');
});

// pagination - load more 
const PaginationButton = document.getElementById('pagination');
const ProductParent = document.getElementById('product_parent_pagination');

if (PaginationButton && ProductParent) {
    PaginationButton.addEventListener('click', function () {
        this.setAttribute('disabled', true); // Disable button
        this.innerText = 'Fetching...';

        let CurrentPage = parseInt(PaginationButton.getAttribute('data-page') || 1);
        CurrentPage++;

        fetch(`/home`, {
            method: 'POST',
            body: JSON.stringify({ currentPage: CurrentPage }),
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.is_more_page) {
                    this.removeAttribute('disabled'); // Enable button again
                    this.innerText = 'Show More';
                } else {
                    this.innerText = 'No More Data';
                    this.setAttribute('disabled', false);
                }

                // Make HTML and append to the product container
                let productHTML = '';
                data.books.forEach(book => {
                    productHTML += `
                    <div class="each_product">
                        <div class="product_img_container">
                            <img class="img_product" src="static/img/open_black_book.svg" />
                        </div>
                        <div class="product_content">
                            <h2 class="product_title" title="${book.Title}">${book.truncate_title}</h2>
                            <h3 class="category">${book.Genre}</h3>
                            <div class="price_and_buy">
                                <button class="btn custom_btn"><a href="book_detail/${book.book_id}">Read More</a></button>
                            </div>
                        </div>
                    </div>
                `;
                });

                ProductParent.innerHTML += productHTML; // Append new products to the list

                // Update the button page attribute
                PaginationButton.setAttribute("data-page", CurrentPage);
            })
            .catch(error => {
                console.error('Error loading more books:', error);
                this.removeAttribute('disabled');
                this.innerText = 'Show More';
            });
    });
}


// generate book description on observer 
document.addEventListener("DOMContentLoaded", function () {
    const descriptionElement = document.querySelector(".desc");
    if (descriptionElement) {
        // Observer to detect when `.desc` is in view
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    // Trigger the API request
                    const title = document.querySelector(".product_title").textContent.trim();
                    const author = document.querySelector(".publisher_authour strong[title='author']").textContent.trim();

                    const prompt = `Generate a description for the book: "${title}" by ${author}, up to 400 words.`;

                    fetch("/generate_description", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({ generate_for: prompt }),
                    })
                        .then((response) => response.json())
                        .then((data) => {
                            if (data.description) {
                                descriptionElement.textContent = data.description;
                            } else {
                                descriptionElement.textContent = "Failed to generate description.";
                            }
                        })
                        .catch((error) => {
                            console.error("Error generating description:", error);
                            descriptionElement.textContent = "Error loading description.";
                        });

                    // Stop observing after request is sent
                    observer.unobserve(descriptionElement);
                }
            });
        });

        observer.observe(descriptionElement);
    }
});
