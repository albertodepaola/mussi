var wc = {
    divLinkAttributesHTMLContent: '<div class="row">' +
                    '    <div class="col-xs-12">' +
                    '        <div class="form-group">' +
                    '            <label for="link-action">Acción</label>' +
                    '            <input type="text" class="form-control" id="link-action" name="link-action" placeholder="Nombre de la acción">' +
                    '        </div>' +
                    '    </div>' +
                    '    <div class="col-xs-12">' +
                    '        <div class="checkbox">' +
                    '            <label>' +
                    '                <input id="link-execute-automatically" name="link-execute-automatically" type="checkbox">' +
                    '                <b>Ejecutar automaticamente</b>' +
                    '            </label>' +
                    '        </div>' +
                    '        <div id="link-execute-automatically-details">' +
                    '            <label for="link-execute-automatically-time"><i class="fa fa-clock-o"></i> Después de</label><br>' +
                    '            <input type="number" min="1" max="999" step="1" id="link-execute-automatically-time" name="link-execute-automatically-time">' +
                    '            <select id="link-execute-automatically-time-unit" name="link-execute-automatically-time-unit">' +
                    '                <option value="h"> Horas</option>' +
                    '                <option value="d"> Días</option>' +
                    '            </select><br>' +
                    '            <label for="link-execute-automatically-time"> Disparar acciones: </label>&nbsp;&nbsp;' +
                    '            <label><input id="link-unlink-automatically" name="link-unlink-automatically" type="checkbox"> <b>Quitar agente a cargo</b></label>&nbsp;' +
                    '            <label><input id="link-notify-automatically" name="link-notify-automatically" type="checkbox"> <b>Notificar</b></label>&nbsp;' +
                    '            <label><input id="link-notify-email-automatically" name="link-notify-email-automatically" type="checkbox"> <b>Enviar email</b></label>' +
                    '        </div>' +
                    '    </div>' +
                    '    <div class="col-xs-12">' +
                    '        <div class="checkbox">' +
                    '            <label>' +
                    '                <input id="link-inverse" name="link-inverse" type="checkbox">' +
                    '                <b>Acción inversa</b>' +
                    '            </label>' +
                    '        </div>' +
                    '        <div id="link-inverse-details" class="row">' +
                    '            <div class="col-xs-12">' +
                    '                <div class="form-group">' +
                    '                    <input type="text" class="form-control" id="link-inverse-action" name="link-inverse-action" placeholder="Nombre de la acción">' +
                    '                </div>' +
                    '            </div>' +
                    '            <div class="col-xs-12">' +
                    '                <div class="checkbox">' +
                    '                    <label>' +
                    '                        <input id="link-inverse-execute-automatically" name="link-inverse-execute-automatically" type="checkbox">' +
                    '                        <b>Ejecutar automaticamente</b>' +
                    '                    </label>' +
                    '                </div>' +
                    '                <div id="link-inverse-execute-automatically-details">' +
                    '                    <label for="link-inverse-execute-automatically-time"><i class="fa fa-clock-o"></i> Después de</label><br>' +
                    '                    <input type="number" min="1" max="999" step="1" id="link-inverse-execute-automatically-time" name="link-inverse-execute-automatically-time">' +
                    '                    <select id="link-inverse-execute-automatically-time-unit" name="link-inverse-execute-automatically-time-unit">' +
                    '                        <option value="h"> Horas</option>' +
                    '                        <option value="d"> Días</option>' +
                    '                    </select><br>' +
                    '                    <label for="link-inverse-execute-automatically-time"> Disparar acciones: </label>&nbsp;&nbsp;' +
                    '                    <label><input id="link-inverse-unlink-automatically" name="link-inverse-unlink-automatically" type="checkbox"> <b>Quitar agente a cargo</b></label>&nbsp;' +
                    '                    <label><input id="link-inverse-notify-automatically" name="link-inverse-notify-automatically" type="checkbox"> <b>Notificar</b></label>&nbsp;' +
                    '                    <label><input id="link-inverse-notify-email-automatically" name="link-inverse-notify-email-automatically" type="checkbox"> <b>Enviar email</b></label>' +
                    '                </div>' +
                    '            </div>' +
                    '        </div>' +
                    '    </div>' +
                    '</div>',
    rgbBlackWhiteContrast: function(rgb) {
        rgb = Array.prototype.join.call(arguments).match(/(-?[0-9\.]+)/g)
        for (var i = 0; i < rgb.length; i++) {
            rgb[i] = (i === 3 ? 1 : 255) - rgb[i]
        }

        var c = 'rgb('+rgb[0]+','+rgb[1]+','+rgb[2]+')'
        var o = Math.round(((parseInt(rgb[0]) * 299) + (parseInt(rgb[1]) * 587) + (parseInt(rgb[2]) * 114)) /1000)

        if(o < 125) {
            return '#000000'
        } else {
            return '#ffffff'
        }
    },
    invertRGB: function(rgb, forceTransparency) {
        rgb = Array.prototype.join.call(arguments).match(/(-?[0-9\.]+)/g);
        for (var i = 0; i < rgb.length; i++) {
            rgb[i] = (i === 3 ? 1 : 255) - rgb[i];
        }
        rgb.pop(rgb.length - 1)
        if (forceTransparency && rgb.length == 4) {
            rgb[rgb.length - 1] = forceTransparency
        }
        rgb = (rgb.length == 4 ? 'rgba(' : 'rgb(') + rgb.join(', ') + ')'
        return rgb
    },
    roundedRect: function(ctx, x, y, width, height, radius, args) {
        var color = args.color
        var fill = args.fill
        var strokeStyle = args.strokeStyle
        var text = args.text
        var textFill = args.textFill
        var font = args.font
        var lineWidth = args.lineWidth

        ctx.beginPath()
        ctx.moveTo(x, y + radius)
        ctx.lineTo(x, y + height - radius)
        ctx.arcTo(x, y + height, x + radius, y + height, radius)
        ctx.lineTo(x + width - radius, y + height)
        ctx.arcTo(x + width, y + height, x + width, y + height - radius, radius)
        ctx.lineTo(x + width, y + radius)
        ctx.arcTo(x + width, y, x + width - radius, y, radius)
        ctx.lineTo(x + radius, y)
        ctx.arcTo(x, y, x, y + radius, radius)

        if (fill) {
            if (color) {ctx.fillStyle = color}
            oldFillStyle = ctx.fillStyle
            ctx.fill()
            ctx.fillStyle = oldFillStyle
        } else {
            oldStrokeStyle = ctx.strokeStyle
            if (color) {ctx.strokeStyle = color}
            ctx.stroke()
        ctx.strokeStyle = oldStrokeStyle
        }

        if (fill && (strokeStyle || lineWidth)) {
          ctx.beginPath()
          ctx.moveTo(x, y + radius)
          ctx.lineTo(x, y + height - radius)
          ctx.arcTo(x, y + height, x + radius, y + height, radius)
          ctx.lineTo(x + width - radius, y + height)
          ctx.arcTo(x + width, y + height, x + width, y + height - radius, radius)
          ctx.lineTo(x + width, y + radius)
          ctx.arcTo(x + width, y, x + width - radius, y, radius)
          ctx.lineTo(x + radius, y)
          ctx.arcTo(x, y, x, y + radius, radius)
          oldStrokeStyle = ctx.strokeStyle
          ctx.strokeStyle = strokeStyle
          oldLineWidth = ctx.lineWidth
          ctx.lineWidth = lineWidth
          ctx.stroke()
          ctx.strokeStyle = oldStrokeStyle
          ctx.lineWidth = oldLineWidth
        }

        if (text) {
            oldFont = ctx.font
            if (font) {ctx.font = font}
            oldFillStyle = ctx.fillStyle
            if (textFill) {ctx.fillStyle = (textFill == 'reverse' && color) ? wc.invertRGB(color, 1) : ((textFill == 'auto') ? wc.rgbBlackWhiteContrast(color) : textFill)}
            ctx.textBaseline = 'middle'
            ctx.textAlign = 'center'
            ctx.fillText(text, x + width / 2, y + height / 2, width * 0.8)
            ctx.fillStyle = oldFillStyle
            ctx.font = oldFont
        }
    },
    straightArrow: function(context, color, lineWidth, fromX, fromY, toX, toY, bidirectional, textFrom, textTo) {
        oldStrokeStyle = context.strokeStyle
        context.strokeStyle = color
        oldLineWidth = context.lineWidth
        context.lineWidth = lineWidth

        var headLength = 8
        var angleTo = Math.atan2(toY - fromY, toX - fromX)
        var angleFrom = angleTo + Math.PI
        var arrowAngle = Math.PI / 8

        context.beginPath()
        context.moveTo(fromX, fromY)
        context.lineTo(toX, toY)
        context.lineTo(toX - headLength * Math.cos(angleTo - arrowAngle), toY - headLength * Math.sin(angleTo - arrowAngle))
        context.moveTo(toX, toY)
        context.lineTo(toX - headLength * Math.cos(angleTo + arrowAngle), toY - headLength * Math.sin(angleTo + arrowAngle))
        if (bidirectional) {
            context.moveTo(fromX, fromY)
            context.lineTo(fromX - headLength * Math.cos(angleFrom - arrowAngle), fromY - headLength * Math.sin(angleFrom - arrowAngle))
            context.moveTo(fromX, fromY)
            context.lineTo(fromX - headLength * Math.cos(angleFrom + arrowAngle), fromY - headLength * Math.sin(angleFrom + arrowAngle))
        }
        context.stroke()

        if (textFrom || textTo) {
            var inverseAngle = angleTo < -(Math.PI / 2) || angleTo > (Math.PI / 2)
            oldFont = context.font
            context.font = '10pt FontAwesome'
            oldFillStyle = context.fillStyle
            context.fillStyle = color
            context.textAlign = 'center'
            context.textBaseline = 'bottom'
            context.translate(fromX + (toX - fromX) / 2 , fromY + (toY - fromY) / 2)
            context.rotate(angleTo + (inverseAngle ? Math.PI : 0))
            if (textFrom) {context.fillText((inverseAngle ? '\uf0a8  ' : '\uf0a9  ') + textFrom + (inverseAngle ? '  \uf0a8' : '  \uf0a9'), 0, -3, Math.abs((fromY - toY) / Math.sin(angleTo)) * .8)}
            context.textBaseline = 'top'
            if (textTo) {context.fillText((inverseAngle ? '\uf0a9  ' : '\uf0a8  ') + textTo + (inverseAngle ? '  \uf0a9' : '  \uf0a8'), 0, 3, Math.abs((fromY - toY) / Math.sin(angleTo)) * .8)}
            context.rotate(-(angleTo + (inverseAngle ? Math.PI : 0)))
            context.translate(-(fromX + (toX - fromX) / 2) , -(fromY + (toY - fromY) / 2))
            context.fillStyle = oldFillStyle
            context.font = oldFont
            context.strokeStyle = oldStrokeStyle
            context.lineWidth = oldLineWidth
        }
    },
    getEventCoordinates: function(e) {
        var x = null
        var y = null
        if (e.layerX && e.layerY) {
            x = e.layerX
            y = e.layerY
        } else if (e.targetTouches) {
            x = e.targetTouches[0].pageX - this.canvasCoordinates().left
            y = e.targetTouches[0].pageY - this.canvasCoordinates().top
        } else if (e.originalEvent) {
            if (e.originalEvent.targetTouches) {
                x = e.originalEvent.targetTouches[0].pageX - this.canvasCoordinates().left
                y = e.originalEvent.targetTouches[0].pageY - this.canvasCoordinates().top
            } else {
                x = e.originalEvent.layerX
                y = e.originalEvent.layerY
            }
        }
        return {x: x, y: y}
    },
    canvasMouseMoveDefault: function(e) {
        this.workflowCanvas.cursor(e)
        if (this.workflowCanvas.movingState) {
            this.workflowCanvas.moveState(e)
        } else if (this.workflowCanvas.creatingLinkFromState) {
            this.workflowCanvas.createLinkFromState(e)
        }
    },
    WorkflowCanvas: function($parentSelector, $preventScrollingSelector) {
        $parentSelector.empty()
        var canvasHTML = '<canvas id="contact-states-workflow-canvas" height="450px" width="950px" style="border: 1px solid #000000; background-color: #ecf0f5">Su navegador no soporta Canvas</canvas>'
        //var $canvas = $('<canvas/>', {id: 'contact-states-workflow-canvas', height: '300px', width: '950px', style: 'border: 1px solid #000000; background-color: #ecf0f5;'}).append('Su navegador no soporta Canvas')
        var $divLinkAttributes = $('<div/>', {id: 'link-attributes', style: 'padding: 5px; border: 1px solid #000000; display: none;'}).append(wc.divLinkAttributesHTMLContent)
        var $canvasRow = $('<div/>', {class: 'row'})
                            .append($('<div/>', {class: 'col-xs-12'}).append(canvasHTML))
                            .append($('<div/>', {class: 'col-xs-12'}).append($divLinkAttributes))
        $parentSelector.append($canvasRow)



        this.getCanvasDOM = $canvasRow.find('canvas').get(0)
        this.getCanvasDOM.workflowCanvas = this
        this.$divLinkAttributes = $divLinkAttributes

        this.$divLinkAttributes.find('input, select').change(function() {
            cnv.workflowCanvas.updateLink()
        })

        this.$divLinkAttributes.find('input#link-execute-automatically').change(function() {
            if ($(this).prop('checked')) {
                $divLinkAttributes.find('div#link-execute-automatically-details').show()
            } else {
                $divLinkAttributes.find('div#link-execute-automatically-details').hide()
            }
        })

        this.$divLinkAttributes.find('input#link-inverse').change(function() {
            if ($(this).prop('checked')) {
                $divLinkAttributes.find('div#link-inverse-details').show()
            } else {
                $divLinkAttributes.find('div#link-inverse-details').hide()
            }
        })

        this.$divLinkAttributes.find('input#link-inverse-execute-automatically').change(function() {
            if ($(this).prop('checked')) {
                $divLinkAttributes.find('div#link-inverse-execute-automatically-details').show()
            } else {
                $divLinkAttributes.find('div#link-inverse-execute-automatically-details').hide()
            }
        })

        this.context = this.getCanvasDOM.getContext('2d')
        this.states = []
        this.links = []
        this.selectedState = null
        this.movingState = null
        this.creatingLinkFromState = null
        this.stateMoved = false
        this.selectedLink = null

        this.canvasCoordinates = function() {
            var elem = this.getCanvasDOM
            var box = elem.getBoundingClientRect()
            var body = document.body
            var docEl = document.documentElement
            var scrollTop = window.pageYOffset || docEl.scrollTop || body.scrollTop
            var scrollLeft = window.pageXOffset || docEl.scrollLeft || body.scrollLeft
            var clientTop = docEl.clientTop || body.clientTop || 0
            var clientLeft = docEl.clientLeft || body.clientLeft || 0
            var top = box.top +  scrollTop - clientTop
            var left = box.left + scrollLeft - clientLeft
            return {
                top: Math.round(top),
                left: Math.round(left)
            }
        }

        this.toJson = function(extraValues) {
            dict = {
                states: $.map(this.states, function(s) {return s.toDict()}),
                links: $.map(this.links, function(l) {return l.toDict()})
            }
            $.each(extraValues, function(key, value) {
                dict[key] = value
            })
            return JSON.stringify(dict)
        }

        this.loadJson = function(json, decoded) {
            var canvas = this
            canvas.clearAll(true)
            data = !decoded ? JSON.parse(json) : json
            var states = {}
            $.each(data.states, function(idx, s) {
                state = new wc.WorkflowState(canvas, s.id, s.text, s.position, s.color)
                states[s.id] = state
            })
            $.each(data.links, function(idx, l) {
                new wc.WorkflowLink(canvas, l.id, states[l.sourceStateId], states[l.targetStateId], l.text, l.automatic, l.inverse, false, true)
            })
        }

        this.generateNewStateId = function() {
            var newId = 1
            $.each(this.states, function(k, state) {
                newId = state.id + 1
            })
            return newId
        }

        this.drawAllStates = function(exclude) {
            $.each(this.states.filter(function(s) {return !exclude || exclude.indexOf(s) == -1}), function(id, s) {
                s.draw()
            })
        }

        this.clearAllStates = function(exclude) {
            $.each(this.states.filter(function(s) {return !exclude || exclude.indexOf(s) == -1}), function(id, s) {
                s.clear()
            })
        }

        this.addState = function(state) {
            this.states.push(state)
            state.draw()
        }

        this.moveState = function(e) {
            eventCoordinates = wc.getEventCoordinates(e)
            this.movingState.moveTo([eventCoordinates.x, eventCoordinates.y])
            this.stateMoved = true
        }

        this.createLinkFromState = function(e) {
            eventCoordinates = wc.getEventCoordinates(e)
            new wc.WorkflowLink(this, 0, this.creatingLinkFromState, [eventCoordinates.x, eventCoordinates.y], '', null, null, true)
        }

        this.clickedState = function(e) {
            eventCoordinates = wc.getEventCoordinates(e)
            states = this.states.filter(function(s) {return eventCoordinates.x >= s.position[0] && eventCoordinates.x <= s.position[0] + s.size[0] && eventCoordinates.y >= s.position[1] && eventCoordinates.y <= s.position[1] + s.size[1]})
            if (states.length > 0) {
                return states[0]
            } else {
                return null
            }
        }

        this.clickedColor = function(e) {
            eventCoordinates = wc.getEventCoordinates(e)
            if (this.selectedState && this.selectedState.colorPallet) {
                return this.selectedState.colorFromCoordinates([eventCoordinates.x, eventCoordinates.y])
            }
            return null
        }

        this.clickedLink = function(e) {
            eventCoordinates = wc.getEventCoordinates(e)
            var link = null
            $.each(this.links, function(idx, l) {
                ctx = l.invisibleClickableRectangle()
                if (ctx.isPointInPath(eventCoordinates.x, eventCoordinates.y)) {
                    link = l
                    return false
                }
            })
            return link
        }

        this.setSelectedState = function(state) {
            this.unselectStates()
            state.highlight()
            this.selectedState = state
        }

        this.setSelectedLink = function(link) {
            this.unselectLinks()
            link.highlight()
            this.selectedLink = link
            this.$divLinkAttributes.attr('link-id', link.id).show().css('border', '3px solid blue')
            var canvas = this
            setTimeout(function() {canvas.$divLinkAttributes.css('border', '1px solid #000000')}, 3000)

            this.$divLinkAttributes.find('input#link-action').val(link.text)
            this.$divLinkAttributes.find('input#link-execute-automatically').prop('checked', link.automatic)

            if (link.automatic) {
                this.$divLinkAttributes.find('input#link-execute-automatically-time').val(link.automatic.time)
                this.$divLinkAttributes.find('select#link-execute-automatically-time-unit').val(link.automatic.unit)
                this.$divLinkAttributes.find('input#link-unlink-automatically').prop('checked', link.automatic.unlinkAgent)
                this.$divLinkAttributes.find('input#link-notify-automatically').prop('checked', link.automatic.notify)
                this.$divLinkAttributes.find('input#link-notify-email-automatically').prop('checked', link.automatic.email)
            } else {
                this.$divLinkAttributes.find('input#link-execute-automatically-time').val(null)
                this.$divLinkAttributes.find('select#link-execute-automatically-time-unit').val('h')
                this.$divLinkAttributes.find('input#link-unlink-automatically').prop('checked', false)
                this.$divLinkAttributes.find('input#link-notify-automatically').prop('checked', false)
                this.$divLinkAttributes.find('input#link-notify-email-automatically').prop('checked', false)
            }

            this.$divLinkAttributes.find('input#link-inverse').prop('checked', link.inverse)
            if (link.inverse) {
                this.$divLinkAttributes.find('input#link-inverse-action').val(link.inverse.text)
                this.$divLinkAttributes.find('input#link-inverse-execute-automatically').prop('checked', link.inverse.automatic)

                if (link.inverse.automatic) {
                    this.$divLinkAttributes.find('input#link-inverse-execute-automatically-time').val(link.inverse.automatic.time)
                    this.$divLinkAttributes.find('select#link-inverse-execute-automatically-time-unit').val(link.inverse.automatic.unit)
                    this.$divLinkAttributes.find('input#link-inverse-unlink-automatically').prop('checked', link.inverse.automatic.unlinkAgent)
                    this.$divLinkAttributes.find('input#link-inverse-notify-automatically').prop('checked', link.inverse.automatic.notify)
                    this.$divLinkAttributes.find('input#link-inverse-notify-email-automatically').prop('checked', link.inverse.automatic.email)
                } else {
                    this.$divLinkAttributes.find('input#link-inverse-execute-automatically-time').val(null)
                    this.$divLinkAttributes.find('select#link-inverse-execute-automatically-time-unit').val('h')
                    this.$divLinkAttributes.find('input#link-inverse-unlink-automatically').prop('checked', false)
                    this.$divLinkAttributes.find('input#link-inverse-notify-automatically').prop('checked', false)
                    this.$divLinkAttributes.find('input#link-inverse-notify-email-automatically').prop('checked', false)
                }
            } else {
                this.$divLinkAttributes.find('input#link-inverse-action').val(null)
                this.$divLinkAttributes.find('input#link-inverse-execute-automatically').prop('checked', false)
                this.$divLinkAttributes.find('input#link-inverse-execute-automatically-time').val(null)
                this.$divLinkAttributes.find('select#link-inverse-execute-automatically-time-unit').val('h')
                this.$divLinkAttributes.find('input#link-inverse-unlink-automatically').prop('checked', false)
                this.$divLinkAttributes.find('input#link-inverse-notify-automatically').prop('checked', false)
                this.$divLinkAttributes.find('input#link-inverse-notify-email-automatically').prop('checked', false)
            }

            this.$divLinkAttributes.find('input#link-execute-automatically').trigger('change')
            this.$divLinkAttributes.find('input#link-inverse').trigger('change')
            this.$divLinkAttributes.find('input#link-inverse-execute-automatically').trigger('change')
        }

        this.enableMove = function(e) {
            state = this.clickedState(e)
            if (state) {
                if (state != this.selectedState) {
                    this.creatingLinkFromState = null
                    this.movingState = state
                } else {
                    this.movingState = null
                    this.creatingLinkFromState = state
                }
            } else {
                this.creatingLinkFromState = null
                this.movingState = null
            }
        }

        this.selectElement = function(e) {
            state = this.clickedState(e)
            color = this.clickedColor(e)
            if (state && !color) {
                this.unselectLinks()
                if (!this.selectedState) {
                    if (!this.stateMoved) {
                        this.setSelectedState(state)
                    }
                } else if (this.selectedState != state) {
                    var canvas = this
                    if (this.links.filter(function(l) {return (l.sourceState == canvas.selectedState && l.targetState == state) || (l.sourceState == state && l.targetState == canvas.selectedState)}).length == 0) {
                        new wc.WorkflowLink(this, 0, this.selectedState, state, 'Nueva acción', null ,null)
                    } else {
                        this.setSelectedState(state)
                    }
                }
            } else if (color) {
                this.selectedState.changeColor(color)
            } else {
                this.unselectStates()
                link = this.clickedLink(e)
                if (link) {
                    this.setSelectedLink(link)
                } else {
                    this.unselectLinks()
                }
            }
        }

        this.deleteSelectedElement = function() {
            var canvas = this
            if (this.selectedState) {
                this.states = this.states.filter(function(s) {return s != canvas.selectedState})
                this.links = this.links.filter(function(l) {return l.sourceState != canvas.selectedState && l.targetState != canvas.selectedState})
                this.selectedState = null
                this.clearAll()
                this.drawAll()
            }
            if (this.selectedLink) {
                this.links = this.links.filter(function(l) {return l != canvas.selectedLink})
                this.unselectLinks()
                this.selectedLink = null
                this.clearAll()
                this.drawAll()
            }
        }

        this.cursor = function(e) {
            state = this.clickedState(e)
            link = this.clickedLink(e)
            if (link || state) {
                this.getCanvasDOM.style.cursor = 'pointer'
            } else {
                this.getCanvasDOM.style.cursor = 'default'
            }
        }

        this.unselectStates = function() {
            $.each(this.states, function(k, s) {
                s.changeTextFromInput()
            })

            if (this.selectedState) {
                this.selectedState.removeHighlight()
                this.selectedState = null
            }
        }

        this.unselectLinks = function() {
            if (this.selectedLink) {
                this.selectedLink.removeHighlight()
                this.selectedLink = null
                this.$divLinkAttributes.attr('link-id', null).hide()
            }
        }

        this.doubleClickHandler = function(e) {
            eventCoordinates = wc.getEventCoordinates(e)
            state = this.clickedState(e)
            if (state) {
                state.editTextOn()
            } else {
                new wc.WorkflowState(this, 0, 'Nuevo estado', [eventCoordinates.x, eventCoordinates.y], [127, 127, 127])
            }
        }

        this.generateNewLinkId = function() {
            var newId = 1
            $.each(this.links, function(k, link) {
                newId = link.id + 1
            })
            return newId
        }

        this.clearAllLinks = function(exclude) {
            $.each(this.links.filter(function(l) {return !exclude || exclude.indexOf(l) == -1}), function(id, l) {
                l.clear()
            })
        }

        this.drawAllLinks = function(exclude) {
            $.each(this.links.filter(function(l) {return !exclude || exclude.indexOf(l) == -1}), function(id, l) {
                l.draw()
            })
        }

        this.addLink = function(link, dontSelect) {
            this.links.push(link)
            this.clearAll()
            this.drawAll()
            if (!dontSelect && !link.temp) {
                this.unselectStates()
                this.setSelectedLink(link)
            }
        }

        this.updateLink = function() {
            link = this.selectedLink
            if (link && parseInt(this.$divLinkAttributes.attr('link-id')) == link.id) {
                link.text = this.$divLinkAttributes.find('input#link-action').val()
                link.automatic = (this.$divLinkAttributes.find('input#link-execute-automatically').prop('checked') && parseInt(this.$divLinkAttributes.find('input#link-execute-automatically-time').val())) ? {
                    time: parseInt(this.$divLinkAttributes.find('input#link-execute-automatically-time').val()),
                    unit: this.$divLinkAttributes.find('select#link-execute-automatically-time-unit').val(),
                    unlinkAgent: this.$divLinkAttributes.find('input#link-unlink-automatically').prop('checked'),
                    notify: this.$divLinkAttributes.find('input#link-notify-automatically').prop('checked'),
                    email: this.$divLinkAttributes.find('input#link-notify-email-automatically').prop('checked')
                } : null

                link.inverse = this.$divLinkAttributes.find('input#link-inverse').prop('checked') ? {
                    text: this.$divLinkAttributes.find('input#link-inverse-action').val(),
                    automatic: (this.$divLinkAttributes.find('input#link-inverse-execute-automatically').prop('checked') && parseInt(this.$divLinkAttributes.find('input#link-inverse-execute-automatically-time').val())) ? {
                        time: parseInt(this.$divLinkAttributes.find('input#link-inverse-execute-automatically-time').val()),
                        unit: this.$divLinkAttributes.find('select#link-inverse-execute-automatically-time-unit').val(),
                        unlinkAgent: this.$divLinkAttributes.find('input#link-inverse-unlink-automatically').prop('checked'),
                        notify: this.$divLinkAttributes.find('input#link-inverse-notify-automatically').prop('checked'),
                        email: this.$divLinkAttributes.find('input#link-inverse-notify-email-automatically').prop('checked')
                    } : null
                } : null

                this.clearAll()
                this.drawAll()
            }
        }

        this.drawAll = function(exclude) {
            this.drawAllStates(exclude)
            this.drawAllLinks(exclude)
        }

        this.clearAll = function(destroyInnerObjects) {
            this.links = this.links.filter(function(l) {return !l.erase})
            if (destroyInnerObjects) {
                this.states = []
                this.links = []
            }
            this.context.clearRect(0, 0, this.getCanvasDOM.width, this.getCanvasDOM.height)
        }

        this.hasIsolatedStates = function() {
            return this.states.filter(function(s) {return s.isolated()}).length > 0
        }

        this.hasNoInitialState = function() {
            return this.states.filter(function(s) {return s.initialState()}).length == 0
        }

        this.hasManyInitialStates = function() {
            return this.states.filter(function(s) {return s.initialState()}).length > 1
        }

        $(this.getCanvasDOM).click(function(e) {this.workflowCanvas.selectElement(e)})
        $(this.getCanvasDOM).mousedown(function(e) {this.workflowCanvas.enableMove(e)})
        $(this.getCanvasDOM).mouseup(function(e) {
            var workflowCanvas = this.workflowCanvas
            workflowCanvas.movingState = null
            workflowCanvas.creatingLinkFromState = null
            setTimeout(function() {workflowCanvas.stateMoved = false}, 500)
        })
        $(this.getCanvasDOM).mousemove(wc.canvasMouseMoveDefault)
        $(this.getCanvasDOM).dblclick(function(e) {this.workflowCanvas.doubleClickHandler(e)})
        var canvas = this
        $(document).keydown(function(e) {if (e.keyCode == 46) {canvas.deleteSelectedElement()}})
        $(document).click(function(e) {
            if (!(e.target == canvas.getCanvasDOM || e.target == canvas.$divLinkAttributes || $(e.target).is('#' + canvas.$divLinkAttributes.attr('id') + ' *'))) {
                canvas.unselectStates()
                canvas.unselectLinks()
            }
        })

        // Prevent scrolling when touching the canvas
        var cnv = this.getCanvasDOM
        $preventScrollingSelector.on('touchstart', function (e) {if (e.target == cnv) {e.preventDefault()}})
        $preventScrollingSelector.on('touchmove', function (e) {if (e.target == cnv) {e.preventDefault()}})
        $preventScrollingSelector.on('touchend', function (e) {if (e.target == cnv) {e.preventDefault()}})
    },
    workflowStateSize: [200, 30],
    workflowStateRadius: 10,
    workflowStateTransparency: 0.6,
    workflowStateFontStyle: 'bold 12pt Calibri',
    colorPalletConfig: {
        colorsPerRow: 13,
        redSequence: [1, 1, 1, .5, 0, 0, 0, 0, 0, .5, 1, 1, 0],
        greenSequence: [0, .5, 1, 1, 1, 1, 1, .5, 0, 0, 0, 0, 0],
        blueSequence: [0, 0, 0, 0, 0, .5, 1, 1, 1, 1, 1, .5, 0],
        rows: 2,
        rowValues: [153, 255],
        lastValues: [0, 255],
        rowHeight: 10,
        separationFromState: 3
    },
    WorkflowState: function(canvas, id, text, position, color) {
        this.canvas = canvas
        this.id = parseInt(id) ? parseInt(id) : canvas.generateNewStateId()
        this.text = text
        this.position = position
        this.color = color
        this.size = wc.workflowStateSize
        this.radius = wc.workflowStateRadius
        this.transparency = wc.workflowStateTransparency
        this.fontStyle = wc.workflowStateFontStyle
        this.highlighted = false
        this.input = null
        this.colorPallet = false
        this.colorPalletConfig = wc.colorPalletConfig

        this.toDict = function() {
            return {
                id: this.id,
                text: this.text,
                position: this.position,
                color: this.color
            }
        }

        this.rgba = function() {
            return 'rgba(' + this.color.join(', ') + ', ' + this.transparency + ')'
        }

        this.draw = function(clearFirst) {
            if (clearFirst) {
                this.clear()
            }
            wc.roundedRect(this.canvas.context, this.position[0], this.position[1], this.size[0], this.size[1], this.radius, {color: this.rgba(), fill: true, strokeStyle: 'rgb(' + (this.isolated() ? '255' : '0') + ', ' + (this.initialState() ? '255' : '0') + ', 0)', lineWidth: this.highlighted ? 2 : 1, text: this.text, textFill: 'auto', font: this.fontStyle})
        }

        this.isolated = function() {
            var thisState = this
            return this.canvas.links.filter(function(l) {return l.sourceState == thisState || l.targetState == thisState}).length == 0
        }

        this.initialState = function() {
            var thisState = this
            return !this.isolated() && this.canvas.links.filter(function(l) {return l.targetState == thisState}).length == 0
        }

        this.clear = function() {
            this.canvas.context.clearRect(this.position[0] - 2, this.position[1] - 2, this.size[0] + 4, this.size[1] + 4)
            this.clearColorPallet()
            this.colorPallet = false
        }

        this.moveTo = function(newPosition) {
            this.canvas.clearAll()
            this.position = [newPosition[0] - this.size[0] / 2, newPosition[1] - this.size[1] / 2]
            this.canvas.drawAll()
        }

        this.changeText = function(newText) {
            this.text = newText
            this.draw(true)
        }

        this.changeTextFromInput = function() {
            if (this.input) {
                var newValue = this.input.value().trim()
                if (newValue) {this.changeText(newValue)}
                this.input.blur()
                this.input.destroy()
                this.input.render()
                this.input = null
                this.canvas.clearAll()
                this.canvas.drawAll()
            }
        }

        this.showColorPallet = function() {
            var colorsPerRow = this.colorPalletConfig.colorsPerRow
            var redSequence = this.colorPalletConfig.redSequence
            var greenSequence = this.colorPalletConfig.greenSequence
            var blueSequence = this.colorPalletConfig.blueSequence
            var rows = this.colorPalletConfig.rows
            var rowValues = this.colorPalletConfig.rowValues
            var lastValues = this.colorPalletConfig.lastValues
            var rowHeight = this.colorPalletConfig.rowHeight
            var separationFromState = this.colorPalletConfig.separationFromState

            var colors = colorsPerRow * rows

            var oldFillStyle = this.canvas.context.fillStyle
            var oldStrokeStyle = this.canvas.context.strokeStyle
            this.canvas.context.strokeStyle = '#000000'

            for (i = 1; i <= colors; i++) {
                var red = parseInt((i % colorsPerRow) != 0 ? redSequence[(i - 1) % colorsPerRow] * rowValues[~~((i - 1) / colorsPerRow)] : lastValues[~~((i - 1) / colorsPerRow)])
                var green = parseInt((i % colorsPerRow) != 0 ? greenSequence[(i - 1) % colorsPerRow] * rowValues[~~((i - 1) / colorsPerRow)] : lastValues[~~((i - 1) / colorsPerRow)])
                var blue = parseInt((i % colorsPerRow) != 0 ? blueSequence[(i - 1) % colorsPerRow] * rowValues[~~((i - 1) / colorsPerRow)] : lastValues[~~((i - 1) / colorsPerRow)])
                this.canvas.context.fillStyle = 'rgb(' + red + ',' + green + ',' + blue + ')'
                var width = this.size[0] / colorsPerRow
                var height = rowHeight
                var x = this.position[0] + ((i - 1) % colorsPerRow) * width
                var y = this.position[1] + this.size[1] + separationFromState + ~~((i - 1) / colorsPerRow) * rowHeight
                this.canvas.context.beginPath()
                this.canvas.context.rect(x, y, width, height)
                this.canvas.context.stroke()
                this.canvas.context.fill()
                this.canvas.context.closePath()
            }

            this.canvas.context.fillStyle = oldFillStyle
            this.canvas.context.strokeStyle = oldStrokeStyle
        }

        this.palletCoordinates = function() {
            var coordinates = {
                position: [0, 0],
                size: [0, 0]
            }
            if (this.colorPallet) {
                coordinates.position[0] = this.position[0]
                coordinates.position[1] = this.position[1] + this.size[1] + this.colorPalletConfig.separationFromState
                coordinates.size[0] = this.size[0]
                coordinates.size[1] = this.colorPalletConfig.rows * this.colorPalletConfig.rowHeight
            }
            return coordinates
        }

        this.clearColorPallet = function() {
            if (this.colorPallet) {
                this.canvas.context.clearRect(this.palletCoordinates().position[0] - 2, this.palletCoordinates().position[1] - 2, this.palletCoordinates().size[0] + 4, this.palletCoordinates().size[1] + 4)
            }
        }

        this.colorFromCoordinates = function(coordinates) {
            color = this.color
            palletCoordinates = this.palletCoordinates()
            x = coordinates[0] - palletCoordinates.position[0]
            y = coordinates[1] - palletCoordinates.position[1]
            if (this.colorPallet && x <= palletCoordinates.size[0] && y <= palletCoordinates.size[1]) {
                var rowNum = ~~(y / this.colorPalletConfig.rowHeight)
                var colorBoxWidth = this.size[0] / this.colorPalletConfig.colorsPerRow
                var colorBoxNum = ~~(x / colorBoxWidth)

                var red = parseInt(((colorBoxNum % (this.colorPalletConfig.colorsPerRow - 1)) != 0 || !colorBoxNum) ? this.colorPalletConfig.redSequence[colorBoxNum] * this.colorPalletConfig.rowValues[rowNum] : this.colorPalletConfig.lastValues[rowNum])
                var green = parseInt(((colorBoxNum % (this.colorPalletConfig.colorsPerRow - 1)) != 0 || !colorBoxNum) ? this.colorPalletConfig.greenSequence[colorBoxNum] * this.colorPalletConfig.rowValues[rowNum] : this.colorPalletConfig.lastValues[rowNum])
                var blue = parseInt(((colorBoxNum % (this.colorPalletConfig.colorsPerRow - 1)) != 0 || !colorBoxNum) ? this.colorPalletConfig.blueSequence[colorBoxNum] * this.colorPalletConfig.rowValues[rowNum] : this.colorPalletConfig.lastValues[rowNum])
                color = [red, green, blue]
            }

            return color
        }

        this.changeColor = function(newColor) {
            this.color = newColor
            this.draw(true)
        }

        this.setColorFromCoordinates = function(coordinates) {
            this.changeColor(this.colorFromCoordinates(coordinates))
        }

        this.editTextOn = function() {
            var state = this
            this.input = new CanvasInput({
                canvas: this.canvas.getCanvasDOM,
                x: this.position[0] + this.size[0] * .05,
                y: this.position[1],
                width: this.size[0] * .825,
                height: this.size[1] / 2,
                value: this.text,
                onsubmit: function() {
                    state.changeTextFromInput()
                }
            })
            this.input.focus()
            this.showColorPallet()
            this.colorPallet = true
        }

        this.highlight = function() {
            this.transparency = 1
            this.highlighted = true
            this.canvas.clearAll()
            this.canvas.drawAll()
        }

        this.removeHighlight = function() {
            this.transparency = wc.workflowStateTransparency
            this.highlighted = false
            this.canvas.clearAll()
            this.canvas.drawAll()
        }

        this.topPoint = function(offset) {
            offset = offset ? offset : 0
            return [this.position[0] + this.size[0] / 2, this.position[1] - offset]
        }

        this.topRightPoint = function(offset) {
            offset = offset ? offset : 0
            return [this.position[0] + this.size[0] + offset, this.position[1] - offset]
        }

        this.rightPoint = function(offset) {
            offset = offset ? offset : 0
            return [this.position[0] + this.size[0] + offset, this.position[1] + this.size[1] / 2]
        }

        this.bottomRightPoint = function(offset) {
            offset = offset ? offset : 0
            return [this.position[0] + this.size[0] + offset, this.position[1] + this.size[1] + offset]
        }

        this.bottomPoint = function(offset) {
            offset = offset ? offset : 0
            return [this.position[0] + this.size[0] / 2, this.position[1] + this.size[1] + offset]
        }

        this.bottomLeftPoint = function(offset) {
            offset = offset ? offset : 0
            return [this.position[0] - offset, this.position[1] + this.size[1] + offset]
        }

        this.leftPoint = function(offset) {
            offset = offset ? offset : 0
            return [this.position[0] - offset, this.position[1] + this.size[1] / 2]
        }

        this.topLeftPoint = function(offset) {
            offset = offset ? offset : 0
            return [this.position[0] - offset, this.position[1] - offset]
        }

        this.canvas.addState(this)
    },
    workflowLinkLineWidth: 1,
    workflowStateFontStyle: '10pt Calibri',
    workflowHighlightedLinkRGB: 'rgb(0, 50, 255)',
    WorkflowLink: function(canvas, id, sourceState, targetState, text, automatic, inverse, temp, dontSelect) {
        this.canvas = canvas
        this.id = parseInt(id) ? parseInt(id) : canvas.generateNewLinkId()
        this.sourceState = sourceState
        this.targetState = targetState
        this.text = text
        this.automatic = automatic
        this.inverse = inverse
        this.lineWidth = wc.workflowLinkLineWidth
        this.fontStyle = wc.workflowStateFontStyle
        this.highlighted = false
        this.input = null
        this.temp = temp ? temp : false
        this.erase = false

        this.rgb = function() {
            return this.highlighted ? wc.workflowHighlightedLinkRGB : 'rgb(0, 0, 0)'
        }

        this.toDict = function() {
            return {
                id: this.id,
                sourceStateId: this.sourceState.id,
                targetStateId: this.targetState.id,
                text: this.text,
                automatic: this.automatic ? {
                    time: this.automatic.time,
                    unit: this.automatic.unit,
                    unlinkAgent: this.automatic.unlinkAgent,
                    notify: this.automatic.notify,
                    email: this.automatic.email
                } : null,
                inverse: this.inverse ? {
                    text: this.inverse.text,
                    automatic: this.inverse.automatic ? {
                        time: this.inverse.automatic.time,
                        unit: this.inverse.automatic.unit,
                        unlinkAgent: this.inverse.automatic.unlinkAgent,
                        notify: this.inverse.automatic.notify,
                        email: this.inverse.automatic.email
                    } : null,
                } : null,
            }
        }

        this.hasTarget = function() {
            return this.targetState.__proto__.constructor.name == 'WorkflowState'
        }

        this.getCoordinates = function() {
            offsetLineDrawing = 2 //offset is set for lines not to touch the states boxes
            offsetForAngleCalculations = 5 //offset is set for lines not to have extremely sharp angles

            if (this.hasTarget()) {
                targetLeftPoint = this.targetState.leftPoint()
                targetLeftPointLineDrawingOffset = this.targetState.leftPoint(offsetLineDrawing)
                targetLeftPointAngleCalcOffset = this.targetState.leftPoint(offsetForAngleCalculations)

                targetTopPoint = this.targetState.topPoint()
                targetTopPointLineDrawingOffset = this.targetState.topPoint(offsetLineDrawing)
                targetTopPointAngleCalcOffset = this.targetState.topPoint(offsetForAngleCalculations)

                targetRightPointLineDrawingOffset = this.targetState.rightPoint(offsetLineDrawing)

                targetBottomPointLineDrawingOffset = this.targetState.bottomPoint(offsetLineDrawing)
                targetBottomPointAngleCalcOffset = this.targetState.bottomPoint(offsetForAngleCalculations)
            } else {
                targetLeftPoint = this.targetState
                targetLeftPointLineDrawingOffset = this.targetState
                targetLeftPointAngleCalcOffset = this.targetState

                targetTopPoint = this.targetState
                targetTopPointLineDrawingOffset = this.targetState
                targetTopPointAngleCalcOffset = this.targetState

                targetRightPointLineDrawingOffset = this.targetState

                targetBottomPointLineDrawingOffset = this.targetState
                targetBottomPointAngleCalcOffset = this.targetState
            }

            left = this.sourceState.leftPoint()[0] < targetLeftPoint[0]
            above = this.sourceState.topPoint()[1] < targetTopPoint[1]
            if (above && left) {
                if (Math.atan((this.sourceState.bottomPoint(offsetForAngleCalculations)[0] - targetTopPointAngleCalcOffset[0]) / (this.sourceState.bottomPoint(offsetForAngleCalculations)[1] - targetTopPointAngleCalcOffset[1])) < -(Math.PI / 4)) {
                    return [this.sourceState.rightPoint(offsetLineDrawing)[0], this.sourceState.rightPoint(offsetLineDrawing)[1], targetLeftPointLineDrawingOffset[0], targetLeftPointLineDrawingOffset[1]]
                } else {
                    return [this.sourceState.bottomPoint(offsetLineDrawing)[0], this.sourceState.bottomPoint(offsetLineDrawing)[1], targetTopPointLineDrawingOffset[0], targetTopPointLineDrawingOffset[1]]
                }
            } else if (above && !left) {
                if (Math.atan((this.sourceState.bottomPoint(offsetForAngleCalculations)[0] - targetTopPointAngleCalcOffset[0]) / (this.sourceState.bottomPoint(offsetForAngleCalculations)[1] - targetTopPointAngleCalcOffset[1])) > (Math.PI / 4)) {
                    return [this.sourceState.leftPoint(offsetLineDrawing)[0], this.sourceState.leftPoint(offsetLineDrawing)[1], targetRightPointLineDrawingOffset[0], targetRightPointLineDrawingOffset[1]]
                } else {
                    return [this.sourceState.bottomPoint(offsetLineDrawing)[0], this.sourceState.bottomPoint(offsetLineDrawing)[1], targetTopPointLineDrawingOffset[0], targetTopPointLineDrawingOffset[1]]
                }
            } else if (!above && left) {
                if (Math.atan((this.sourceState.topPoint(offsetForAngleCalculations)[0] - targetBottomPointAngleCalcOffset[0]) / (this.sourceState.topPoint(offsetForAngleCalculations)[1] - targetBottomPointAngleCalcOffset[1])) > (Math.PI / 4)) {
                    return [this.sourceState.rightPoint(offsetLineDrawing)[0], this.sourceState.rightPoint(offsetLineDrawing)[1], targetLeftPointLineDrawingOffset[0], targetLeftPointLineDrawingOffset[1]]
                } else {
                    return [this.sourceState.topPoint(offsetLineDrawing)[0], this.sourceState.topPoint(offsetLineDrawing)[1], targetBottomPointLineDrawingOffset[0], targetBottomPointLineDrawingOffset[1]]
                }
            } else if (!above && !left) {
                if (Math.atan((this.sourceState.topPoint(offsetForAngleCalculations)[0] - targetBottomPointAngleCalcOffset[0]) / (this.sourceState.topPoint(offsetForAngleCalculations)[1] - targetBottomPointAngleCalcOffset[1])) < -(Math.PI / 4)) {
                    return [this.sourceState.leftPoint(offsetLineDrawing)[0], this.sourceState.leftPoint(offsetLineDrawing)[1], targetRightPointLineDrawingOffset[0], targetRightPointLineDrawingOffset[1]]
                } else {
                    return [this.sourceState.topPoint(offsetLineDrawing)[0], this.sourceState.topPoint(offsetLineDrawing)[1], targetBottomPointLineDrawingOffset[0], targetBottomPointLineDrawingOffset[1]]
                }
            }

            return null
        }

        this.clear = function() {
        }

        this.draw = function(clearFirst) {
            if (this.temp) {
                this.canvas.clearAll()
                this.canvas.drawAll([this])
            }
            if (clearFirst) {
                this.clear()
            }
            coordinates = this.getCoordinates()
            if (coordinates) {
                wc.straightArrow(this.canvas.context, this.rgb(), this.lineWidth, coordinates[0], coordinates[1], coordinates[2], coordinates[3], this.inverse, this.text + (this.automatic ? ('  \uf017' + this.automatic.time + this.automatic.unit) : ''), this.inverse ? (this.inverse.text + (this.inverse.automatic ? ('  \uf017' + this.inverse.automatic.time + this.inverse.automatic.unit) : '')) : null)
            }
            if (this.temp) {
                this.erase = true
            }
        }

        this.invisibleClickableRectangle = function() {
            var r = this.getLineCoordinates()
            this.canvas.context.save()
            this.canvas.context.beginPath()
            this.canvas.context.translate(r.translateX, r.translateY)
            this.canvas.context.rotate(r.rotation)
            this.canvas.context.rect(r.rectX, r.rectY, r.rectWidth, r.rectHeight)
            this.canvas.context.translate(-r.translateX, -r.translateY)
            this.canvas.context.rotate(-r.rotation)
            this.canvas.context.fillStyle = 'transparent'
            this.canvas.context.strokeStyle = 'transparent'
            this.canvas.context.fill()
            this.canvas.context.stroke()
            this.canvas.context.restore()
            return this.canvas.context
        }

        this.getLineCoordinates = function() {
            var dx = this.getCoordinates()[2] - this.getCoordinates()[0]; // deltaX used in length and angle calculations
            var dy = this.getCoordinates()[3] - this.getCoordinates()[1]; // deltaY used in length and angle calculations
            var lineLength = Math.sqrt(dx * dx + dy * dy)
            var lineRadianAngle = Math.atan2(dy, dx)
            var invisibleLineWidth = 5

            return ({
                translateX: this.getCoordinates()[0],
                translateY: this.getCoordinates()[1],
                rotation: lineRadianAngle,
                rectX: 0,
                rectY: -invisibleLineWidth / 2,
                rectWidth: lineLength,
                rectHeight: invisibleLineWidth
            })
        }

        this.highlight = function() {
            this.lineWidth = 2
            this.highlighted = true
            this.canvas.clearAll()
            this.canvas.drawAll()
        }

        this.removeHighlight = function() {
            this.lineWidth = 1
            this.highlighted = false
            this.canvas.clearAll()
            this.canvas.drawAll()
        }

        this.canvas.addLink(this, dontSelect)
    }
}