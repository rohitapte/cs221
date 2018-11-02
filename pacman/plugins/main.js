// Include this script to include everything you need.

(function() {
  var head = document.getElementsByTagName('head')[0];

  function includeScript(src, text) {
    var script = document.createElement('script');
    script.src = src;
    if (text) script.text = text;
    head.appendChild(script);
    return script;
  }

  function includeStylesheet(href) {
    var css = document.createElement('link');
    css.setAttribute('rel', 'stylesheet');
    css.setAttribute('href', href);
    head.appendChild(css);
    return css;
  }

  function initMathJax(scriptLocation, fallbackScriptLocation) {
    if (typeof(sfig) != 'undefined') return;  // Already loaded through sfig
    var script = includeScript(scriptLocation);
    var buf = '';
    buf += 'MathJax.Hub.Config({';
    buf += '  extensions: ["tex2jax.js", "TeX/AMSmath.js", "TeX/AMSsymbols.js"],';
    buf += '  tex2jax: {inlineMath: [["$", "$"]]},';
    buf += '});';
    script.innerHTML = buf;

    // If fail, try the fallback location
    script.onerror = function() {
      if (fallbackScriptLocation)
        initMathJax(fallbackScriptLocation, null);
    }
  }

  initMathJax('https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=default');

  includeScript('plugins/jquery.min.js');
  includeStylesheet('plugins/main.css');
})();

function fixScrollPosition() {
  var store = {};
  if (typeof(localStorage) != 'undefined' && localStorage != null) store = localStorage;

  var scrollTopKey = window.location.pathname+'.scrollTop';
  // Because we insert MathJax, we lose the scrolling position, so we have to
  // put it back manually.
  window.onscroll = function() {
    store[scrollTopKey] = document.body.scrollTop;
  }
  if (store.scrollTop)
    window.scrollTo(0, store[scrollTopKey]);
}

function onLoad(assignmentId, ownerName, version) {
  // Insert generic text
  var header = $('#assignmentHeader');

  header.append($('<div>')
    .append($('<div>', {class: 'assignmentTitle'}).append(document.title))
    .append($('<div>').append('Stanford CS221 Fall 2017-2018'.bold())));
  header.append($('<p>').append('Owner CA: ' + ownerName));
  header.append($('<p>').append('Version: ' + version));

  header.append('<hr>');
  header.append($('<div>', {class: 'problemTitle'}).append('General Instructions'));

  header.append($('<p>').append('This (and every) assignment has a written part and a programming part.'));
  header.append($('<p>').append('The full assignment with our supporting code and scripts can be downloaded as <a href="../' + assignmentId + '.zip">' + assignmentId + '.zip</a>.'));
  var ol = $('<ol>').addClass('problem');
  ol.append($('<li>').addClass('writeup').addClass('template').append('This icon means a written answer is expected in <code>' + assignmentId + '.pdf</code>.'));
  ol.append($('<li>').addClass('code').addClass('template').append('This icon means you should write code in <code>submission.py</code>.'));
  header.append(ol);

  header.append($('<p>').append(
    'You should modify the code in <code>submission.py</code> between ' +
    '<pre># BEGIN_YOUR_CODE</pre> and <pre># END_YOUR_CODE</pre> ' +
    'but you can add other helper functions outside this block if you want. ' +
    'Do not make changes to files other than <code>submission.py</code>.'));

  header.append($('<p>').append(
    'Your code will be evaluated on two types of test cases, <b>basic</b> and <b>hidden</b>, which you can see in <code>grader.py</code>. ' +
    'Basic tests, which are fully provided to you, do not stress your code with large inputs or tricky corner cases. ' +
    'Hidden tests are more complex and do stress your code.  The inputs of hidden tests are provided in <code>grader.py</code>, but the correct outputs are not. ' +
    'To run the tests, you will need to have <code>graderUtil.py</code> in the same directory as your code and <code>grader.py</code>. ' +
    'Then, you can run all the tests by typing <pre>python grader.py</pre> ' +
    'This will tell you only whether you passed the basic tests. ' +
    'On the hidden tests, the script will alert you if your code takes too long or crashes, but does not say whether you got the correct output. ',
    'You can also run a single test (e.g., <code>3a-0-basic</code>) by typing <pre>python grader.py 3a-0-basic</pre>',
    'We strongly encourage you to read and understand the test cases, create your own test cases, and not just blindly run <code>grader.py</code>.'));

  header.append('<hr>');

  // Link to code (any mention of *.py).
  $('code').each(function(i, elem) {
    if (true)  {
      var value = elem.innerHTML;
      if (value.match(/.py$/))
        elem.innerHTML = '<a href="' + value + '">' + value + '</a>';
    }
  });

  // Render point values
  var maxPoints = {};  // Part to number of maxPoints
  function updatePoints(part) {
    var partName = part['name'].split('-')[0];
    maxPoints[partName] = (maxPoints[partName] || 0) + part['maxPoints'];
  }
  allResult.parts.forEach(updatePoints);

  function showPoints(i, p) {
    if (!p.attributes.id) {
      console.log("Missing id attribute in", p);
      return;
    }
    var partName = p.attributes.id.value;
    var n = maxPoints[partName];
    var s = '[' + n + ' point' + (n > 1 ? 's' : '') + ']';
    $(p).prepend(s);
  }
  $('.writeup').not('.template').each(showPoints);
  $('.code').not('.template').each(showPoints);

  fixScrollPosition();
}
