// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  // lesson Model
  // ----------

  // Our basic **lesson** model has `title`, `subtitle`, `duration`, `subject` and `updated` attributes.
  window.Lesson = Backbone.Model.extend({

    idAttribute: "_id",

    // If you don't provide a lesson, one will be provided for you.
    EMPTY: "no lesson available",

    // Ensure that each lesson created has `content`.
    initialize: function() {
      if (!this.get("title")) {
        this.set({"title": this.EMPTY});
      }
    },


    // Remove this Lesson from *localStorage* and delete its view.
    clear: function() {
      this.destroy();
      this.view.remove();
    }

  });

  // Lesson Collection
  // ---------------Ï
  window.LessonList = Backbone.Collection.extend({

    // Reference to this collection's model.
    model: Lesson,

    url: '/v1/curriculum/' + $("#currid").val() + '/lessons',

    // We keep the Lesson in sequential order, despite being saved by unordered
    // GUID in the database. This generates the next order number for new items.
    nextOrder: function() {
      if (!this.length) return 1;
      return this.last().get('order') + 1;
    },

    // Lesson are sorted by their original insertion order.
    comparator: function(lesson) {
      return lesson.get('order');
    }

  });

  // Create our global collection of **Lesson**.
  window.Lessons = new LessonList;

  // Lesson Item View
  // --------------

  // The DOM element for a lesson item...
  window.LessonView = Backbone.View.extend({

    //... is a list tag.
    tagName:  "li",

    // Cache the template function for a single item.
    template: _.template($('#lesson-template').html()),

    // The DOM events specific to an item.
    events: {
      "dblclick div.lesson-content" : "edit",
      "keypress .lesson-input"      : "updateOnEnter"
    },

    // The LessonView listens for changes to its model, re-rendering. Since there's
    // a one-to-one correspondence between a **Lesson** and a **View** in this
    // app, we set a direct reference on the model for convenience.
    initialize: function() {
      _.bindAll(this, 'render', 'close');
      this.model.bind('change', this.render);
      this.model.view = this;
    },

    // Re-render the contents of the lesson item.
    render: function() {
      $(this.el).html(this.template(this.model.toJSON()));
      return this;
    },

    // Switch this view into `"editing"` mode, displaying the input field if we choose to make this editable
    edit: function() {
      $(this.el).addClass("editing");
      this.input.focus();
    },

    // Close the `"editing"` mode, saving changes to the lesson.
    close: function() {
      this.model.save({content: this.input.val()});
      $(this.el).removeClass("editing");
    },

    // If you hit `enter`, we're through editing the lesson.
    //
    updateOnEnter: function(e) {
      if (e.keyCode == 13) this.close();
    },

    // Remove this view from the DOM.
    remove: function() {
      $(this.el).remove();
    },

    // Remove the item, destroy the model.
    clear: function() {
      this.model.clear();
    }

  });

  // The Application
  // ---------------

  // Our overall **AppView** is the top-level piece of UI.
  window.AppView = Backbone.View.extend({

    // Instead of generating a new element, bind to the existing skeleton of
    // the App already present in the HTML.
    el: $("#lessonapp"),

    // Our template for the line of statistics at the bottom of the app.
    statsTemplate: _.template($('#stats-template').html()),

    // Delegated events for creating new items, and clearing completed ones.
    events: {
      "click #submit-lesson" : "new_lesson",
      "click #edit" : "edit_field",
      "click #save" : "save_field"
    },

    // At initialization we bind to the relevant events on the `Lesson`
    // collection, when items are added or changed. Kick things off by
    // loading any preexisting lessons that might be saved in *localStorage*.
    initialize: function() {
      _.bindAll(this,'addOne', 'addAll');
      var handlers = {
          "success": this.addAll,
          "error": function() {console.log("fetch failed")}
         };
      
      Lessons.fetch(handlers);
    },

    // Re-rendering the App just means refreshing the statistics -- the rest
    // of the app doesn't change.
    render: function() {
      this.$('#lesson-stats').html(this.statsTemplate({
        curriculums:  Lessons.length,
      }));
    },

    new_lesson: function(){
      $.post( "/curriculum/" +  $("#currid").val() + "/add_lesson", 
          {'name':$("#_name").val(),
            'subtitle': $("#_subtitle").val(),
            'expectedDuration':$('#_duration').val(),
            'parentId' : $("#_parent").val(),
            'content': $("#_descript").val(),
            'curriculumId' : $("#_curr_id").val(),
            'originalAuthorId' : $("#_original").val()},
        function( data ) {
        location.reload();
      });
    },

    edit_field: function(e) {
      e.preventDefault();
      var data_id = $(e.currentTarget).data("name");
      $('#edit_' + data_id).summernote({focus: true});
    },


    // Add a single lesson item to the list by creating a view for it, and
    // appending its element to the `<ul>`.
    addOne: function(lesson) {
      console.log('add one');
      var view = new LessonView({model: lesson});
      this.$("#lesson-list").append(view.render().el);
    },

    // Add all items in the **Lesson** collection at once.
    addAll: function() {
        console.log('add all');
        Lessons.each(this.addOne);
    },

    // Generate the attributes for a new Lesson item.
    // `title`, `subtitle`, `duration`, `subject` and `updated` attributes.
    newAttributes: function() {
      return {
        title: this.input.val(),
        subtitle:   Lesson.nextOrder(),
        duration: "",
        subject: "",
        updated: "",
      };
    },

    // If you hit return in the main input field, create new **Lesson** model,
    // persisting it to *localStorage*.
    createOnEnter: function(e) {
      if (e.keyCode != 13) return;
      Lesson.create(this.newAttributes());
      this.input.val('');
    },

    // Clear all finished Lesson items, destroying their models.
    // hypothetical
    // clearCompleted: function() {
    //   _.each(Lesson.deleted, function(curriculum){ lesson.clear(); });
    //   return false;
    // },

  });

  // Finally, we kick things off by creating the **App**.
  window.App = new AppView;

});
