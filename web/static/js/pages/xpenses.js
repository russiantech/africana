$(document).ready(() => {
    //I'm extending jquery so I can make $.delete()/$.put()  request with this short-cut syntax ($.delete() )
    jQuery.each(["put", "delete"], function (i, method) {
        jQuery[method] = function (url, data, callback, type) {
            if (jQuery.isFunction(data)) {
                type = type || callback;
                callback = data;
                data = undefined;
            }
    
            return jQuery.ajax({
                url: url,
                type: method,
                dataType: type,
                data: data,
                success: callback
            });
        };
    });

    var newrow =
            `
            <tr role="row" class="even"> 
            {% if xpenseform.item_id.errors %}
            <div class="invalid-feedback"> {% for error in xpenseform.item_id.errors %}{{ error }} ! {% endfor %}</div>
            {% else %}
            {{ xpenseform.item_id(hidden=True, value=0,) }}
            {% endif %}

            <td class="id"><input type='text' value="##" disabled name="id" class='disabled form-control' /></td>

        <td class="cate">{% if xpenseform.type.errors %}
            <div class="invalid-feedback"> {% for error in xpenseform.type.errors %}{{ error }} ! {% endfor %}</div>
            {% else %}
            {{ xpenseform.type(class='form-control') }}
            {% endif %}</td>
    
            <td class="cost">{% if xpenseform.cost.errors %}
            <div class="invalid-feedback"> {% for error in xpenseform.cost.errors %}{{ error }} ! {% endfor %}</div>
            {% else %}
            {{ xpenseform.cost(class='form-control', placeholder='Amount Spent') }}
            {% endif %}</td>
    
            <td class="comment">{% if xpenseform.comment.errors %}
            <div class="invalid-feedback"> {% for error in xpenseform.comment.errors %}{{ error }} ! {% endfor %}</div>
            {% else %}
            {{ xpenseform.comment(class='form-control', placeholder="briefly describe what you spent on") }}
            {% endif %}</td> 

            <td class="created">{% if xpenseform.created.errors %}
            <div class="invalid-feedback"> {% for error in xpenseform.created.errors %}{{ error }} ! {% endfor %}</div>
            {% else %}
            {{ xpenseform.created(class='form-control') }}
            {% endif %}</td> 

            <td class="list_action">
            <div class="d-flex align-items-center list-action">
            <button type="submit" id="save" class="badge badge-info mr-2 border-0" data-toggle="tooltip"
            data-placement="top" title="Save it" data-original-title="Save"><i class="las la-plus mr-0"></i>
            </button> 
            <button type="button" id="cancel" class="badge bg-warning mr-2 border-0" data-toggle="tooltip"
            data-placement="top" title="Cancel" data-original-title="Delete"><i class="ri-delete-bin-line mr-0"></i></button>
    
            </div>
            </td>  
    
        </tr>
                ` ;
    
    var edit_action_btn = `<button type="button" id="edit" class="border-0 badge bg-success mr-2" data-toggle="tooltip"
                                    data-placement="top" title="" data-original-title="Edit">
                                    <i class="ri-pencil-line mr-0"></i></button>
            `
    
    $(".add-list").click( () => { $("tbody").prepend(newrow); }); // appending dynamic string/<tr> to table tbody
    
    $('tbody').on('click', '#cancel', () => { $('tbody #cancel').parent().parent().parent().remove() });
    
    const url = "{{url_for('endpoint.xpenses_action')}}";
    
    $('#xpensesform').submit((e) => {
            alert('xpensesform-form-submissions')
            e.preventDefault()
    
            $('#response').html('<i class="fa fa-circle-notch fa-spin fa-1x fa-fw"></i>');
            save_btn = $('#save').html()
            //alert($('td').find('#item_id').val())
            var jqxhr = $.post(url, $('form').serialize());
    
            jqxhr.done((r) => {
                //alert("ajax success");
                //
                $('#save').html(save_btn); //reset spinning submit-btn
                frondend_save(); //appends-new-row-added()
                if ('undefined' != typeof (r.response)) {
                    $('#response').html((r.response)).addClass(r.flash);
                } else ($('#response').text(r).addClass('alert-success'))
    
    
                if ("undefined" != typeof r.link) {
                    $('#response').append(' -> <br> <a href=' + r.link + '> Continue Here </a>');
                    //$('form').hide();
                }
                if ("undefined" != typeof r.receipt) {
                    $('#response').append('<br> <a href= ' + r.receipt + '> Receipt Here</a>');
                    //$('form').hide();
                }
    
                console.log('response->(' + response.response + 'flash-message (' + response.flash);
    
            });
    
            jqxhr.fail((er) => { //JSON.stringify(err)
                //$('#response').text('oops!!!, Could Not Add This Food. Pls Try Again'+JSON.stringify(er), er).addClass('alert-danger')
                $('#response').text('oops!!!, Could Not Add This Food. Pls Try Again', er).addClass('alert-danger')
                $('#save').html(save_btn); //reset spinning submit-btn
            });
    
            jqxhr.always(() => {
                //alert("ajax complete");
                $('#save').html('<i class="fa fa-circle-notch fa-spin fa-1x fa-fw"></i>');
            });
    
    
        });
    
    frondend_save = () => {
                //insted-of rerender, simply replace the input elements with corresponding val()
                variety = $('td').find('input[name=varieties]').val()
                $('td').find('input[name=varieties]').replaceWith(variety)
                opening = $('td').find('input[name=opening]').val()
                $('td').find('input[name=opening]').replaceWith(opening)
                newstock = $('td').find('input[name=newstock]').val()
                $('td').find('input[name=newstock]').replaceWith(newstock)
                qty = $('td').find('input[name=qty]').val()
                $('td').find('input[name=qty]').replaceWith(qty)
                totalstock = $('td').find('input[name=totalstock]').val()
                $('td').find('input[name=totalstock]').replaceWith(totalstock)
                price = $('td').find('input[name=price]').val()
                $('td').find('input[name=price]').replaceWith(price)
                totalsold = $('td').find('input[name=totalsold]').val()
                $('td').find('input[name=totalsold]').replaceWith(totalsold)
                closingstock = $('td').find('input[name=closingstock]').val()
                $('td').find('input[name=closingstock]').replaceWith(closingstock)
                stockamount = $('td').find('input[name=stockamount]').val()
                $('td').find('input[name=stockamount]').replaceWith(stockamount)
    
                $('td').find('#save').replaceWith(edit_action_btn)
            }
    
    editable = (item_btn) => {
    
                let tr = $(item_btn).closest('tr');
                //let hmm = $(tr).find('td.varieties').html()
                let item_id = $(item_btn).attr('data-id')
    
                const name = $(tr).find("#_name").text();
                const cate = $(tr).find('#_cate').text();
                const in_stock = $(tr).find("#_instock").text();
                const c_price = $(tr).find("#_cprice").text();
                const s_price = $(tr).find("#_sprice").text();
    
                $(tr).replaceWith(newrow);
    
                $('td').find('#item_id').val(item_id)
                $('td').find('#name').val(name)
                $('td').find('#in_stock').val(in_stock)
                $('td').find('#c_price').val(c_price)
                $('td').find('#s_price').val(s_price)
                //$('td').find('#cate').val(cate)
                //for-categori(es)
                $('td').find('#cate option').each((k, v) => {
                    if ($.trim(v.textContent) == $.trim(cate)) {
                        //console.log(k)
                        $('td').find('#cate').val(k)
                    }
                });
    
            }
    
    remove = (del_btn, item_id) => {
    
    _confirm = confirm('This Product/Food Will Be Deleted/Removed, Are You U Really Wanna Do This ?')
    
    if (!_confirm) { return } //true/false
    
    $('#response').html('<i class="fa fa-circle-notch fa-spin fa-1x fa-fw"></i> deleting');
    
    //del_btn = $('#del').html()
    del_btnhtml = $(del_btn).html()
    
    /* window.food_url = "{{url_for('endpoint.stock_action')}}"
    url = window.food_url + "?item_id=" + item_id + "&action=del" */
    
    let url = "{{url_for('endpoint.stock_action')}}"
    url += "?item_id=" + item_id + "&action=del"
    
    var jqxhr = $.delete(url);
    
    jqxhr.done((r) => {
    
        $(del_btn).closest('tr').remove()
        //console.log($(del_btn).closest("tr").html())
    
        $(del_btn).html(del_btnhtml); //reset spinning submit-btn
        //frondend_save(); //appends-new-row-added()
    
        if ('undefined' != typeof (r.response)) {
            $('#response').html((r.response)).addClass(r.flash);
        } else ($('#response').text(r).addClass('alert-success'))
    
        if ("undefined" != typeof r.link) {
            $('#response').append(' -> <br> <a href=' + r.link + '> Continue Here </a>');
        }
        if ("undefined" != typeof r.receipt) {
            $('#response').append('<br> <a href= ' + r.receipt + '> Receipt Here</a>');
        }
    
        //console.log('response->(' + r.response + 'flash-message (' + r.flash); 
    
    });
    
    jqxhr.fail((er) => {
        $('#response').text('oops!!!, Could Not Remove This Food, Request failed. Pls Try Again', er).addClass('alert-danger')
        $(del_btn).html(del_btnhtml);
    });
    
    jqxhr.always(() => {
        //alert("ajax complete");
        $(del_btn).html('<i class="fa fa-circle-notch fa-spin fa-1x fa-fw"></i>');
    });
    
    
    }
    
    
    });
    