

   


(function($){
    $(function(){
  
        
  
      
  
    

    var bar = document.getElementById('js-progressbar');
    
    setTimeout(function() {
        //your code to be executed after 1 second
        var element = document.getElementById('reviewform').click();
        
      }, 1000);
    

    // $('#emailform').submit(function(event){

    //     var email = $('#email').val();
    //     event.stopPropagation();
    //     event.preventDefault();
    //     $.ajax({
    //         url:  '/loginemail',
    //         data: {'email':email},
    //         type: 'POST',
    //         success: function(response){
    //             console.log(response)
    //         }
    //     })

    // });

    $('#emailform').submit(function(){

        $('#emailform').prop('hidden', true);
        $('#formspinner').prop('hidden', false);

    });


    
    $('#review').click(function(){

        var yes = $('#yes').val();
        var text = $('#textarea').val();
        console.log(text);

        $.ajax({
            url:'/review',
            data:{'yes':yes, 'text':text},
            type: 'POST',
            success: function(){
                $('#textarea').val('');
            }

        })


    });

    $('#predictform').submit(function(){

        $('#uploadform').attr("hidden",true);
        $('#uploadtitle').attr("hidden",true);
        $('#predictprogress').attr("hidden",false);
        
        var progbar = document.getElementById('predictprogress');

        var animate = setInterval(function () {

            progbar.value += 2;

            if (progbar.value >= progbar.max) {
                clearInterval(animate);
            }

        }, 2000);



        


    });

    UIkit.upload('#file', {

        url: '/csvupload',
        multiple: false,
        name: 'file',
        allow: '*.csv',
        

        beforeSend: function () {
            console.log('beforeSend', arguments);
        },
        beforeAll: function () {
            console.log('beforeAll', arguments);
            var filename = $('#file').val().split('\\').pop();
            $('#filename').text(' '+filename+' ');
        },
        load: function () {
            console.log('load', arguments);
            
            
        },
        error: function () {
            console.log('error', arguments);
            
        },
        complete: function () {
            console.log('complete', arguments);
            
            
            

        

        },

        loadStart: function (e) {
            console.log('loadStart', arguments);

            bar.removeAttribute('hidden');
            bar.max = e.total;
            bar.value = e.loaded;

            
            
            
        },

        progress: function (e) {
            console.log('progress', arguments);

            bar.max = e.total;
            bar.value = e.loaded;
        },

        loadEnd: function (e) {
            console.log('loadEnd', arguments);

            bar.max = e.total;
            bar.value = e.loaded;

            

            
        },

        completeAll: function () {
            console.log('completeAll', arguments);

            setTimeout(function () {
                bar.setAttribute('hidden', 'hidden');
            }, 2000);

            $('#filenamediv').attr("hidden",false);
            
            alert('Upload Completed');
        }

    });
  
      
  
    }); // end of document ready
  
  })(jQuery); // end of jQuery name space
  
  
  
  
  
  