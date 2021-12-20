

   

(function($){
    $(function(){
  
        
  
      
  
    UIkit.modal("#instructions").show();

    var bar = document.getElementById('js-progressbar');

    $('#predictform').submit(function(){

        $('#uploadform').attr("hidden",true);
        $('#uploadtitle').attr("hidden",true);
        $('#spinner').attr("hidden",false);

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

            alert('Upload Completed');
        }

    });
  
      
  
    }); // end of document ready
  
  })(jQuery); // end of jQuery name space
  
  
  
  
  
  